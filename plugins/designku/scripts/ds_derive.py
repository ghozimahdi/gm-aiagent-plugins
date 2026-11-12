#!/usr/bin/env python3
"""designku derive: create a custom system (customize an existing one or start
from scratch) and save it at user level: ~/.designku/systems/<id>/.

Tonal palettes are regenerated from the seed color(s) by the token engine, the
result is validated against WCAG 2.2, then tokens.json, README.md and
preview.html are written. Pure python3 stdlib.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import shutil

import dslib as L
import ds_builtins
import ds_engine
import ds_preview
import ds_validate

FONT_STYLES = {
    "modern": ("Inter", "Inter"),
    "geometric": ("Manrope", "Inter"),
    "friendly": ("Plus Jakarta Sans", "Plus Jakarta Sans"),
    "soft": ("Outfit", "Figtree"),
    "playful": ("Baloo 2", "Nunito"),
    "elegant": ("Fraunces", "DM Sans"),
    "editorial": ("Playfair Display", "Source Sans 3"),
    "technical": ("IBM Plex Sans", "IBM Plex Sans"),
    "bold": ("Sora", "Be Vietnam Pro"),
    "accessible": ("Atkinson Hyperlegible", "Atkinson Hyperlegible"),
    "readable": ("Lexend", "Lexend"),
}

# Tried in order until the error color is distinguishable from the primary (red/pink/orange brands).
ERROR_ALTERNATIVES = ["#BA1A1A", "#B0125A", "#A8006A", "#B53D00"]


def add_arguments(p: argparse.ArgumentParser) -> None:
    p.add_argument("--base", help="existing system id to start from (omit to start from scratch)")
    p.add_argument("--id", help="new system id (default: slug of --name)")
    p.add_argument("--name", required=True, help="display name")
    p.add_argument("--primary", help="brand / seed color, hex")
    p.add_argument("--secondary", help="optional secondary seed, hex (derived from primary + mood when omitted)")
    p.add_argument("--tertiary", help="optional accent seed, hex")
    p.add_argument("--mood", choices=sorted(ds_engine.MOODS), help="drives derived secondary/tertiary and neutral tint")
    p.add_argument("--neutral-chroma", type=float, help="0 (pure grey) .. 0.03 (clearly tinted)")
    p.add_argument("--neutral-hue", type=float, help="OKLCH hue of neutrals; default = primary hue")
    p.add_argument("--font-style", choices=sorted(FONT_STYLES), help="preset pairing")
    p.add_argument("--font-display", help="Google Font family for display/headline")
    p.add_argument("--font-body", help="Google Font family for body/label")
    p.add_argument("--font-mono", help="Google Font family for mono")
    p.add_argument("--corner", choices=sorted(ds_engine.CORNERS))
    p.add_argument("--density", choices=sorted(ds_engine.DENSITIES))
    p.add_argument("--motion", choices=sorted(ds_engine.MOTIONS))
    p.add_argument("--elevation", choices=sorted(ds_engine.ELEVATIONS))
    p.add_argument("--dark-style", choices=["tinted", "oled"])
    p.add_argument("--contrast", choices=["AA", "AAA"], help="AAA = 7:1 text (low-vision / outdoor / elderly audiences)")
    p.add_argument("--context", help="industry / product context")
    p.add_argument("--audience", help="who uses it")
    p.add_argument("--personality", help="comma separated adjectives")
    p.add_argument("--tagline")
    p.add_argument("--force", action="store_true", help="overwrite an existing custom system with the same id")
    p.add_argument("--dry-run", action="store_true", help="validate only, write nothing")


def _auto_rationale(meta: dict, spec: dict, base: dict | None) -> dict:
    fonts = spec["fonts"]
    _, chroma, hue = L.hex_to_oklch(spec["primary"])
    family = ("neutral grey" if chroma < 0.04 else
              next(name for limit, name in ((40, "red"), (75, "orange"), (110, "yellow"), (165, "green"), (215, "teal"),
                                            (275, "blue"), (320, "violet"), (350, "magenta"), (361, "red")) if hue < limit))
    origin = f"Derived from {base['name']}; " if base else ""
    return {
        "color": f"{origin}tonal palettes are generated from the seed {spec['primary']} (a {family}, OKLCH hue {hue:.0f}°) with CIE L* tone steps, "
                 f"so every on-color pair meets WCAG 2.2 {spec['contrast']} in light and dark. Mood '{spec['mood']}' sets how saturated the "
                 "secondary/tertiary accents and the neutral tint are.",
        "typography": f"{fonts['display']} for display and headlines, {fonts['body']} for body and labels, on the Material 3 type scale.",
        "shape": f"'{spec['corner']}' corners with '{spec['density']}' density; interactive targets never go below 48px.",
        "motion": f"'{spec['motion']}' motion profile.",
    }


def derive(args: argparse.Namespace) -> int:
    base = None
    if args.base:
        base = L.find_system(args.base)
        if not base:
            print(f"error: base system '{args.base}' not found. Run `designku.py list`.")
            return 2
    new_id = L.slugify(args.id or args.name)
    target = L.custom_dir() / new_id
    builtin_ids = {s["id"] for s in L.list_systems() if s["source"] == "builtin"}
    if new_id in builtin_ids:
        print(f"error: '{new_id}' is a built-in id. Choose another --id / --name.")
        return 2
    if target.exists() and not args.force and not args.dry_run:
        print(f"error: custom system '{new_id}' already exists at {target}. Use --force to overwrite or pick another id.")
        return 2

    base_meta = L.meta(base["tokens"]) if base else {}
    spec = copy.deepcopy(base_meta.get("spec") or ds_engine.DEFAULT_SPEC)
    if not base and not args.primary:
        print("error: --primary <hex> is required when creating from scratch.")
        return 2
    for color in (args.primary, args.secondary, args.tertiary):
        if color:
            try:
                L.hex_to_rgb(color)
            except ValueError as exc:
                print(f"error: {exc}")
                return 2
    if args.primary:
        spec["primary"] = args.primary.upper()
        # A new brand color invalidates the base accents and tone overrides: re-derive them.
        spec["secondary"] = None
        spec["tertiary"] = None
        spec["neutralHue"] = None
        spec["tones"] = {"light": {}, "dark": {}}
        spec["error"] = ds_engine.DEFAULT_SPEC["error"]
        # Near-black / graphite brands: keep the primary dark instead of a washed-out mid grey.
        if L.hex_to_oklch(args.primary)[1] < 0.03 and L.tone_of(args.primary) < 30:
            spec["tones"] = {"light": {"primary": 20}, "dark": {"primary": 90}}
    if args.secondary:
        spec["secondary"] = args.secondary.upper()
    if args.tertiary:
        spec["tertiary"] = args.tertiary.upper()
    if args.mood:
        spec["mood"] = args.mood
        spec["neutralChroma"] = ds_engine.MOODS[args.mood][3]
    if args.neutral_chroma is not None:
        spec["neutralChroma"] = max(0.0, min(0.03, args.neutral_chroma))
    if args.neutral_hue is not None:
        spec["neutralHue"] = args.neutral_hue % 360
    fonts = dict(spec.get("fonts") or ds_engine.DEFAULT_SPEC["fonts"])
    if args.font_style:
        fonts["display"], fonts["body"] = FONT_STYLES[args.font_style]
    if args.font_display:
        fonts["display"] = args.font_display
    if args.font_body:
        fonts["body"] = args.font_body
    if args.font_mono:
        fonts["mono"] = args.font_mono
    spec["fonts"] = fonts
    for key, value in (("corner", args.corner), ("density", args.density), ("motion", args.motion),
                       ("elevation", args.elevation), ("darkStyle", args.dark_style), ("contrast", args.contrast)):
        if value:
            spec[key] = value
    spec = ds_engine.merge_spec(ds_engine.DEFAULT_SPEC, spec)
    # merge_spec drops None, so make "derive it" explicit again.
    if args.primary and not args.secondary:
        spec["secondary"] = None
    if args.primary and not args.tertiary:
        spec["tertiary"] = None

    personality = [p.strip() for p in (args.personality or "").split(",") if p.strip()] or base_meta.get("personality", [])
    meta = {
        "id": new_id,
        "name": args.name,
        "letter": "",
        "group": "custom",
        "context": args.context or base_meta.get("context", ""),
        "tagline": args.tagline or (f"Custom system based on {base['name']}." if base else "Custom design system."),
        "audience": args.audience or base_meta.get("audience", ""),
        "personality": personality,
        "createdAt": datetime.date.today().isoformat(),
    }
    if base:
        meta["base"] = base["id"]
        if not args.primary:  # same palette -> the base do/don't still apply
            meta["do"], meta["dont"] = base_meta.get("do", []), base_meta.get("dont", [])
    meta["rationale"] = _auto_rationale(meta, spec, base)

    tokens, errors, warnings = None, [], []
    candidates = [spec["error"]] + [c for c in ERROR_ALTERNATIVES if c != spec["error"]]
    for index, error_seed in enumerate(candidates):
        trial = dict(spec, error=error_seed)
        tokens = ds_engine.build_tokens(meta, trial)
        errors, warnings = ds_validate.validate(tokens)
        if not any("too close to primary" in message for message in errors):
            if index:
                print(f"note: error color moved to {error_seed} to stay distinguishable from the primary.")
            break

    stats = ds_validate.summary(tokens)
    print(f"{args.name} ({new_id})  primary {L.tv(tokens, 'color.light.primary')} / {L.tv(tokens, 'color.dark.primary')}"
          f"  fonts {fonts['display']} / {fonts['body']}")
    print(f"contrast: light min text {stats['light']['minText']:.2f}:1, dark min text {stats['dark']['minText']:.2f}:1 "
          f"({stats['light']['pairs']} pairs per mode, target {spec['contrast']})")
    for message in warnings:
        print("warning: " + message)
    if errors:
        print(f"FAILED validation ({len(errors)}):")
        for message in errors:
            print("  - " + message)
        print("Nothing was saved. Adjust the seed color / options and try again.")
        return 1
    if args.dry_run:
        print("dry run: validation passed, nothing written.")
        return 0

    if target.exists():
        shutil.rmtree(target)
    L.write_json(target / "tokens.json", tokens)
    (target / "README.md").write_text(ds_builtins.readme(tokens), encoding="utf-8")
    system = L.find_system(f"custom:{new_id}")
    preview, _ = ds_preview.ensure_preview(system, force=True)
    print(f"saved:   {target}")
    print(f"preview: {L.file_url(preview)}")
    print(f"next:    /designku:ds-use {new_id}")
    return 0
