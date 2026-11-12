#!/usr/bin/env python3
"""designku CLI — one entry point for every command of the plugin.

  designku.py list      [--json] [--force] [--project DIR]
  designku.py show      [--json] [--project DIR]
  designku.py use       <id> [--output DIR] [--fonts google_fonts|asset] [--no-apply]
  designku.py apply     [--sync] [--no-format] [--project DIR]
  designku.py derive    --name NAME [--base ID] [--primary HEX] ...   (customize / create)
  designku.py validate  [<id|path/to/tokens.json> ...]                (default: every system)
  designku.py preview   [<id> ...] [--all]
  designku.py fonts

Pure python3 stdlib.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dslib as L  # noqa: E402
import ds_catalog  # noqa: E402
import ds_derive  # noqa: E402
import ds_flutter  # noqa: E402
import ds_preview  # noqa: E402
import ds_project  # noqa: E402
import ds_validate  # noqa: E402


def _project(arg: str | None, must_exist_config: bool = False) -> Path | None:
    if arg:
        return Path(arg).expanduser().resolve()
    found = L.find_project_root()
    if found or must_exist_config:
        return found
    return None


def cmd_validate(args) -> int:
    targets = []
    if args.targets:
        for ref in args.targets:
            path = Path(ref).expanduser()
            if path.is_file():
                targets.append((str(path), L.read_json(path)))
                continue
            system = L.find_system(ref)
            if not system:
                print(f"error: '{ref}' is neither a tokens.json path nor a known system id")
                return 2
            targets.append((f"{system['source']}:{system['id']}", system["tokens"]))
    else:
        targets = [(f"{s['source']}:{s['id']}", s["tokens"]) for s in L.list_systems()]
    failed = 0
    for label, tokens in targets:
        errors, warnings = ds_validate.validate(tokens)
        if errors:
            failed += 1
            print(f"FAIL {label}")
            for message in errors:
                print("   - " + message)
        else:
            stats = ds_validate.summary(tokens)
            print(f"PASS {label:<18} {stats['light']['pairs']} pairs/mode · min text {stats['light']['minText']:.2f} light, "
                  f"{stats['dark']['minText']:.2f} dark · min UI {min(stats['light']['minUi'], stats['dark']['minUi']):.2f}")
        if args.verbose:
            for message in warnings:
                print("   warning: " + message)
    print(f"{len(targets) - failed}/{len(targets)} systems pass WCAG 2.2 contrast and structure checks")
    return 1 if failed else 0


def cmd_preview(args) -> int:
    systems = L.list_systems() if (args.all or not args.ids) else []
    for ref in args.ids:
        system = L.find_system(ref)
        if not system:
            print(f"error: system '{ref}' not found")
            return 2
        systems.append(system)
    for system in systems:
        path, regen = ds_preview.ensure_preview(system, force=args.force)
        print(f"{system['id']:<12} {'rendered' if regen else 'fresh   '} {L.file_url(path)}")
    return 0


def cmd_fonts(_args) -> int:
    for family, (kind, note) in L.FONTS.items():
        print(f"{family:<24} {kind:<8} {note}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="designku", description="designku design system CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list built-in + custom systems, refresh previews and the catalog")
    p.add_argument("--json", action="store_true")
    p.add_argument("--force", action="store_true", help="re-render every preview")
    p.add_argument("--project")

    p = sub.add_parser("show", help="show the design system of this project")
    p.add_argument("--json", action="store_true")
    p.add_argument("--project")

    p = sub.add_parser("use", help="set the project default and generate code")
    p.add_argument("id")
    p.add_argument("--project")
    p.add_argument("--output", help="output folder relative to the project root")
    p.add_argument("--platform", default="flutter", choices=["flutter"])
    p.add_argument("--fonts", choices=["google_fonts", "asset"])
    p.add_argument("--no-apply", action="store_true")

    p = sub.add_parser("apply", help="generate platform code from .designku/tokens.json")
    p.add_argument("--project")
    p.add_argument("--sync", action="store_true", help="re-copy tokens from the source system first")
    p.add_argument("--no-format", action="store_true")

    p = sub.add_parser("derive", help="create a custom system in ~/.designku/systems")
    ds_derive.add_arguments(p)

    p = sub.add_parser("validate", help="WCAG + structure validation")
    p.add_argument("targets", nargs="*")
    p.add_argument("-v", "--verbose", action="store_true")

    p = sub.add_parser("preview", help="render preview.html")
    p.add_argument("ids", nargs="*")
    p.add_argument("--all", action="store_true")
    p.add_argument("--force", action="store_true")

    sub.add_parser("fonts", help="list the curated Google Fonts")

    args = parser.parse_args(argv)
    if args.command == "list":
        return ds_catalog.main_list(_project(args.project), args.json, args.force)
    if args.command == "show":
        return ds_project.show(_project(args.project), args.json)
    if args.command == "use":
        project = Path(args.project).expanduser().resolve() if args.project else Path.cwd()
        code = ds_project.use(args.id, project, args.output, args.platform, args.fonts)
        if code == 0 and not args.no_apply:
            code = ds_flutter.apply(project)
        return code
    if args.command == "apply":
        project = _project(args.project, must_exist_config=True) or Path.cwd()
        return ds_flutter.apply(project, sync=args.sync, fmt=not args.no_format)
    if args.command == "derive":
        return ds_derive.derive(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "preview":
        return cmd_preview(args)
    if args.command == "fonts":
        return cmd_fonts(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
