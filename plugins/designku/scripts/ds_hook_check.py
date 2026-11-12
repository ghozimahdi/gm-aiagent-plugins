#!/usr/bin/env python3
"""designku PostToolUse hook: block hardcoded design values in Dart UI code.

Reads the hook payload (JSON) on stdin — Claude Code `Write` / `Edit` /
`MultiEdit`, or Codex `apply_patch`. When an edited .dart file outside the
design-system output folder contains raw colors, text styles or magic spacing,
it prints the offending lines to stderr and exits 2, which feeds the message
back to the agent as blocking feedback.

Does nothing unless the file's project has .designku/config.json.
Escape hatches: `// ds-ignore` on the line (or the line above) and
`// ds-ignore-file` anywhere in the file.

Can also be run by hand:  ds_hook_check.py --scan <file.dart> [...]
Pure python3 stdlib. Never crashes the session: unexpected errors exit 0.
"""
from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import Path

MAX_REPORT = 20
NUM = r"(?<![\w.])(?!0(?:\.0+)?(?![\d.]))\d+(?:\.\d+)?"  # a non-zero numeric literal
NUM_RE = re.compile(NUM)

LINE_RULES = [
    (re.compile(r"\bColor\s*\(\s*0x[0-9A-Fa-f]+"), "raw color",
     "use context.ds.colors.<role> (primary, onSurface, surfaceContainerLow, error, ...)"),
    (re.compile(r"\bColor\.from(?:ARGB|RGBO)\s*\("), "raw color", "use context.ds.colors.<role>"),
    (re.compile(r"\bColors\.(?!transparent\b)[a-zA-Z]\w*"), "Material palette color",
     "use context.ds.colors.<role>; Colors.transparent is the only allowed constant"),
    (re.compile(r"""['"]#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8}|[0-9A-Fa-f]{3})['"]"""), "hex color string",
     "use context.ds.colors.<role>"),
    (re.compile(r"\bfontFamily\s*:"), "hardcoded font family", "use context.ds.text.<role> (fonts come from DsTypography)"),
    (re.compile(r"\bGoogleFonts\.\w+"), "direct google_fonts usage", "use context.ds.text.<role>"),
    (re.compile(r"\bfontSize\s*:\s*" + NUM), "hardcoded font size",
     "use context.ds.text.<role> (bodyMedium, titleLarge, labelSmall, ...) and .copyWith(color: ...) if needed"),
    (re.compile(r"\bBoxShadow\s*\("), "hand-made shadow", "use DsShadows.level1..level5 or DsElevation.levelN"),
    (re.compile(r"\bRadius\.circular\s*\(\s*" + NUM), "magic radius", "use DsRadius.<size>All / DsShape.<component>"),
    (re.compile(r"\bBorderRadius\.circular\s*\(\s*" + NUM), "magic radius", "use DsRadius.<size>All / DsShape.<component>"),
]

# Calls whose numeric arguments must come from spacing tokens. (pattern, label, advice, spacing_only)
CALL_RULES = [
    (re.compile(r"\bEdgeInsets(?:Directional)?\.(?:all|symmetric|only|fromLTRB|fromSTEB)\s*\("), "magic padding",
     "use DsSpacing.<size> or DsInsets.all<Size>/h<Size>/v<Size> (xs 4, sm 8, md 12, lg 16, xl 24, xxl 32)"),
    (re.compile(r"\bSizedBox\s*\("), "magic gap", "use DsGap.<size>() for gaps, or DsSpacing/DsSizes tokens for dimensions"),
]

DEFAULT_IGNORE = ["**/*.g.dart", "**/*.freezed.dart", "**/*.gr.dart", "**/*.config.dart", "**/*.gen.dart",
                  "**/generated/**", "**/l10n/**", "test/**", "**/test/**"]


def find_project(path: Path) -> Path | None:
    for candidate in [path.parent, *path.parent.parents]:
        if (candidate / ".designku" / "config.json").is_file():
            return candidate
    return None


def strip_code(line: str) -> str:
    """Drop // comments and the content of string literals (keeps quotes) for rule matching."""
    out, quote, i = [], None, 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
                out.append(ch)
            i += 1
            continue
        if ch in "'\"":
            quote = ch
            out.append(ch)
        elif ch == "/" and line[i:i + 2] == "//":
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _call_args(code_lines: list[str], line_index: int, start: int) -> list[tuple[int, str]]:
    """(line index, text) pieces of the argument list opened just before `start`."""
    depth, pieces = 1, []
    row, col = line_index, start
    while row < len(code_lines) and row < line_index + 30:
        text = code_lines[row]
        begin = col
        while col < len(text):
            if text[col] == "(":
                depth += 1
            elif text[col] == ")":
                depth -= 1
                if depth == 0:
                    pieces.append((row, text[begin:col]))
                    return pieces
            col += 1
        pieces.append((row, text[begin:]))
        row, col = row + 1, 0
    return pieces


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    """Return (line number, source line, problem, advice) for every violation."""
    if "ds-ignore-file" in text:
        return []
    raw = text.splitlines()
    code = [strip_code(line) for line in raw]
    # strip_code blanks string contents, so the hex-string rule looks at the raw line minus trailing comments
    hex_probe = [re.sub(r"\s//.*$", "", line) for line in raw]
    found: dict[tuple[int, str], tuple[int, str, str, str]] = {}

    def ignored(index: int) -> bool:
        return "ds-ignore" in raw[index] or (index > 0 and raw[index - 1].strip().startswith("//") and "ds-ignore" in raw[index - 1])

    def add(index: int, problem: str, advice: str):
        if not ignored(index):
            found.setdefault((index, problem), (index + 1, raw[index].strip(), problem, advice))

    for index, line in enumerate(code):
        if not line.strip():
            continue
        for pattern, problem, advice in LINE_RULES:
            probe = hex_probe[index] if problem == "hex color string" else line
            if pattern.search(probe):
                add(index, problem, advice)
        for pattern, problem, advice in CALL_RULES:
            for match in pattern.finditer(line):
                pieces = _call_args(code, index, match.end())
                joined = " ".join(piece for _, piece in pieces)
                if problem == "magic gap":
                    if re.search(r"\bchild\s*:", joined):
                        continue  # a sized box around content is layout, not spacing
                    if not re.search(r"\b(?:width|height|dimension)\s*:\s*" + NUM, joined):
                        continue
                for row, piece in pieces:
                    if NUM_RE.search(piece):
                        if problem == "magic gap" and not re.search(r"\b(?:width|height|dimension)\s*:\s*" + NUM, piece):
                            continue
                        add(row, problem, advice)
    return [found[key] for key in sorted(found)]


def _matches(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p.replace("**/", "")) for p in patterns)


def check_file(path: Path, changed: list[str] | None) -> tuple[Path | None, list]:
    """Violations for one file, honoring the project config. `changed` = new text fragments (Edit)."""
    if path.suffix != ".dart" or not path.is_file():
        return None, []
    project = find_project(path)
    if not project:
        return None, []
    try:
        config = json.loads((project / ".designku" / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, []
    enforce = config.get("enforce") or {}
    if enforce.get("enabled") is False:
        return project, []
    rel = path.resolve().relative_to(project.resolve()).as_posix()
    out_dir = ((config.get("output") or {}).get("dir") or "lib/core/design_system").strip("/")
    if rel.startswith(out_dir + "/"):
        return project, []
    if _matches(rel, enforce.get("ignore") or DEFAULT_IGNORE):
        return project, []
    violations = scan_text(path.read_text(encoding="utf-8", errors="replace"))
    if changed is not None and enforce.get("scope", "changed") == "changed":
        fragments = {line.strip() for chunk in changed for line in chunk.splitlines() if line.strip()}
        violations = [v for v in violations if v[1] in fragments]
    return project, violations


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def targets_from_payload(payload: dict) -> list[tuple[Path, list[str] | None]]:
    """(file, changed fragments or None for 'whole file') for the tool call."""
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or ".")
    out: list[tuple[Path, list[str] | None]] = []

    def resolve(p: str) -> Path:
        path = Path(p).expanduser()
        return path if path.is_absolute() else cwd / path

    file_path = tool_input.get("file_path") or tool_input.get("path")
    if isinstance(file_path, str):
        if isinstance(tool_input.get("edits"), list):  # MultiEdit
            changed = [e.get("new_string", "") for e in tool_input["edits"] if isinstance(e, dict)]
        elif isinstance(tool_input.get("new_string"), str):  # Edit
            changed = [tool_input["new_string"]]
        else:  # Write -> the whole file is new
            changed = None
        out.append((resolve(file_path), changed))
        return out
    # Codex apply_patch: the patch text is somewhere in tool_input
    for text in _strings(tool_input):
        if "*** Begin Patch" not in text and "*** Update File:" not in text and "*** Add File:" not in text:
            continue
        current, added = None, []
        for line in text.splitlines():
            header = re.match(r"\*\*\* (?:Add|Update) File: (.+)", line)
            if header or line.startswith("*** "):
                if current:
                    out.append((resolve(current), added))
                current, added = (header.group(1).strip(), []) if header else (None, [])
            elif current and line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:])
        if current:
            out.append((resolve(current), added))
    return out


def report(results: list[tuple[Path, Path, list]]) -> str:
    lines = ["designku: hardcoded design values found — this project uses a design system, do not assume values."]
    shown = 0
    for path, project, violations in results:
        rel = path.resolve().relative_to(project.resolve()).as_posix()
        for number, source, problem, advice in violations:
            if shown >= MAX_REPORT:
                break
            lines.append(f"  {rel}:{number}: {problem}: {source[:110]}")
            lines.append(f"      -> {advice}")
            shown += 1
    total = sum(len(v) for _, _, v in results)
    if total > shown:
        lines.append(f"  ... and {total - shown} more")
    lines.append("Fix: import the design_system barrel and use context.ds.* / Ds* atoms. If a needed token or component does not exist, "
                 "add it to .designku/tokens.json and run /designku:ds-apply — never hardcode. "
                 "Deliberate exception: append `// ds-ignore` to the line.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--scan":
        results = []
        for name in argv[2:]:
            path = Path(name).resolve()
            project, violations = check_file(path, None)
            if project and violations:
                results.append((path, project, violations))
        if results:
            print(report(results), file=sys.stderr)
            return 2
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0
    results = []
    for path, changed in targets_from_payload(payload):
        project, violations = check_file(path, changed)
        if project and violations:
            results.append((path, project, violations))
    if not results:
        return 0
    print(report(results), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # noqa: BLE001 — a hook must never break the session
        sys.exit(0)
