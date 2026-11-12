#!/usr/bin/env python3
"""designku project state: .designku/config.json + .designku/tokens.json.

`use` pins a system to the project by snapshotting its tokens into the repo
(so teammates and CI do not need the plugin or ~/.designku), `show` reports it.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

import dslib as L
import ds_preview

UFIL_COMMON = Path("packages/presentation/feature_common")
DEFAULT_IGNORE = ["**/*.g.dart", "**/*.freezed.dart", "**/*.gr.dart", "**/*.config.dart", "**/*.gen.dart",
                  "**/generated/**", "**/l10n/**", "test/**", "**/test/**"]


def detect_layout(project: Path) -> dict:
    """Where generated Flutter code goes. UFIL modular projects use feature_common."""
    if (project / UFIL_COMMON / "pubspec.yaml").is_file():
        return {
            "layout": "ufil-modular",
            "dir": str(UFIL_COMMON / "lib/src/design_system"),
            "barrel": "design_system.dart",
            "exportFrom": str(UFIL_COMMON / "lib/feature_common.dart"),
            "pubspec": str(UFIL_COMMON / "pubspec.yaml"),
        }
    return {"layout": "single", "dir": "lib/core/design_system", "barrel": "design_system.dart",
            "exportFrom": None, "pubspec": "pubspec.yaml"}


def config_path(project: Path) -> Path:
    return project / L.PROJECT_DIR_NAME / "config.json"


def load_config(project: Path) -> dict | None:
    try:
        return L.read_json(config_path(project))
    except (OSError, ValueError):
        return None


def use(ref: str, project: Path, output: str | None, platform: str, fonts: str | None) -> int:
    system = L.find_system(ref)
    if not system:
        print(f"error: design system '{ref}' not found. Run /designku:ds-list to see the available ids.")
        return 2
    project = project.resolve()
    if platform == "flutter" and not (project / "pubspec.yaml").is_file():
        print(f"error: {project} has no pubspec.yaml — run this from the Flutter project root (or pass --project).")
        return 2
    previous = load_config(project) or {}
    layout = detect_layout(project)
    out = dict(previous.get("output") or layout)
    if not previous.get("output"):
        out = layout
    if output:
        out["dir"] = output
    tokens_text = Path(system["tokens_path"]).read_text(encoding="utf-8")
    config = {
        "version": 1,
        "system": {"id": system["id"], "name": system["name"], "source": system["source"],
                   "checksum": L.sha(tokens_text), "pinnedAt": datetime.date.today().isoformat()},
        "platform": platform,
        "tokens": f"{L.PROJECT_DIR_NAME}/tokens.json",
        "output": out,
        "flutter": {"fonts": fonts or (previous.get("flutter") or {}).get("fonts", "google_fonts")},
        "enforce": previous.get("enforce") or {"enabled": True, "scope": "changed", "ignore": DEFAULT_IGNORE},
    }
    L.write_json(config_path(project), config)
    (project / L.PROJECT_DIR_NAME / "tokens.json").write_text(tokens_text, encoding="utf-8")
    preview, _ = ds_preview.ensure_preview(system)
    print(f"project default: {system['name']} ({system['id']}, {system['source']})")
    print(f"config:  {config_path(project)}")
    print(f"tokens:  {project / L.PROJECT_DIR_NAME / 'tokens.json'} (project snapshot — commit it)")
    print(f"output:  {out['dir']} [{out.get('layout', 'custom')}]")
    print(f"preview: {L.file_url(preview)}")
    return 0


def show(project: Path | None, as_json: bool) -> int:
    if not project:
        print("No design system selected for this project (.designku/config.json not found). Run /designku:ds-list.")
        return 1
    config = load_config(project)
    if not config:
        print("error: .designku/config.json is unreadable.")
        return 1
    system_cfg = config.get("system", {})
    system = L.find_system(f"{system_cfg.get('source')}:{system_cfg.get('id')}")
    info = {"project": str(project), "config": config, "sourceAvailable": bool(system), "preview": None, "drift": None}
    tokens_file = project / config.get("tokens", f"{L.PROJECT_DIR_NAME}/tokens.json")
    if system:
        preview, _ = ds_preview.ensure_preview(system)
        info["preview"] = L.file_url(preview)
        try:
            local = tokens_file.read_text(encoding="utf-8")
            source_sum = L.sha(Path(system["tokens_path"]).read_text(encoding="utf-8"))
            if L.sha(local) != system_cfg.get("checksum"):
                info["drift"] = "project tokens were edited locally (project-specific extensions)"
            elif source_sum != system_cfg.get("checksum"):
                info["drift"] = "the source system changed since it was pinned — run /designku:ds-apply --sync to update"
        except OSError:
            info["drift"] = "project tokens.json is missing — run /designku:ds-use again"
    if as_json:
        print(json.dumps(info, indent=2))
        return 0
    print(f"design system: {system_cfg.get('name')} ({system_cfg.get('id')}, {system_cfg.get('source')})")
    print(f"platform:      {config.get('platform')}")
    print(f"tokens:        {tokens_file}")
    print(f"output:        {project / config.get('output', {}).get('dir', '')}")
    if info["preview"]:
        print(f"preview:       {info['preview']}")
    else:
        print("preview:       source system not found on this machine (the project snapshot still works)")
    if info["drift"]:
        print(f"note:          {info['drift']}")
    return 0
