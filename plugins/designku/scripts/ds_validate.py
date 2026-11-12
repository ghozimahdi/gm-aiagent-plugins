#!/usr/bin/env python3
"""designku validator: WCAG 2.2 contrast + structural checks for a tokens.json.

Pure python3 stdlib. Used by the CLI (`designku.py validate`), by ds_derive.py
before saving a custom system, and by ds_preview.py to print contrast ratios.
"""
from __future__ import annotations

import dslib as L

FAMILIES = ["primary", "secondary", "tertiary", "error", "success", "warning", "info"]
SURFACES = ["surface", "surfaceDim", "surfaceBright", "surfaceContainerLowest", "surfaceContainerLow",
            "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest"]
REQUIRED_ROLES = (
    [f for fam in FAMILIES for f in (fam, "on" + fam.capitalize(), fam + "Container", "on" + fam.capitalize() + "Container")]
    + ["background", "onBackground", "onSurface", "surfaceVariant", "onSurfaceVariant", "outline", "outlineVariant",
       "inverseSurface", "onInverseSurface", "inversePrimary", "scrim", "shadow", "surfaceTint"]
    + SURFACES
)
REQUIRED_TYPE = ["displayLarge", "displayMedium", "displaySmall", "headlineLarge", "headlineMedium", "headlineSmall",
                 "titleLarge", "titleMedium", "titleSmall", "bodyLarge", "bodyMedium", "bodySmall",
                 "labelLarge", "labelMedium", "labelSmall"]
REQUIRED_GROUPS = {
    "spacing": ["none", "xxs", "xs", "sm", "md", "lg", "xl", "xxl", "xxxl", "huge"],
    "radius": ["none", "xs", "sm", "md", "lg", "xl", "full"],
    "shape": ["button", "input", "card", "chip", "dialog", "sheet"],
    "borderWidth": ["none", "thin", "thick", "focus"],
    "elevation": ["level0", "level1", "level2", "level3", "level4", "level5"],
    "iconSize": ["xs", "sm", "md", "lg", "xl"],
    "size": ["touchTarget", "buttonSm", "buttonMd", "buttonLg", "input", "listItem", "appBar", "navBar",
             "avatarSm", "avatarMd", "avatarLg"],
    "opacity": ["disabled", "disabledContainer", "hover", "focus", "pressed", "scrim"],
    "motion.duration": ["instant", "fast", "normal", "slow", "slower"],
    "motion.easing": ["standard", "emphasized", "decelerate", "accelerate"],
}


def contrast_pairs(level: str = "AA") -> list[tuple[str, str, float, str]]:
    """(foreground role, background role, minimum ratio, usage) — identical for light and dark."""
    text = 7.0 if level == "AAA" else 4.5
    ui = 3.0
    pairs: list[tuple[str, str, float, str]] = []
    for fam in FAMILIES:
        cap = fam.capitalize()
        pairs.append((f"on{cap}", fam, text, "text on fill"))
        pairs.append((f"on{cap}Container", f"{fam}Container", text, "text on container"))
    pairs.append(("onBackground", "background", text, "body text"))
    for surface in SURFACES:
        pairs.append(("onSurface", surface, text, "body text"))
    for surface in ["surface", "surfaceVariant", "surfaceContainerLowest", "surfaceContainerLow",
                    "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest"]:
        pairs.append(("onSurfaceVariant", surface, text, "secondary text"))
    pairs.append(("onInverseSurface", "inverseSurface", text, "snackbar text"))
    pairs.append(("inversePrimary", "inverseSurface", text, "snackbar action"))
    for role in ("primary", "error"):
        for surface in ("surface", "surfaceContainerLowest", "surfaceContainerLow", "surfaceContainer"):
            pairs.append((role, surface, text, "colored text / link"))
        for surface in ("surfaceContainerHigh", "surfaceContainerHighest"):
            pairs.append((role, surface, ui, "icon / UI component"))
    for role in ("secondary", "tertiary", "success", "warning", "info"):
        for surface in ("surface", "surfaceContainerLowest", "surfaceContainerLow"):
            pairs.append((role, surface, text, "colored text / status"))
    for surface in SURFACES:
        pairs.append(("outline", surface, ui, "component boundary"))
    return pairs


def measure(tokens: dict, mode: str, level: str = "AA") -> list[dict]:
    rows = []
    for fg, bg, minimum, usage in contrast_pairs(level):
        try:
            fg_hex, bg_hex = L.tv(tokens, f"color.{mode}.{fg}"), L.tv(tokens, f"color.{mode}.{bg}")
        except KeyError:
            continue
        ratio = L.contrast(fg_hex, bg_hex)
        rows.append({"fg": fg, "bg": bg, "fgHex": fg_hex, "bgHex": bg_hex, "ratio": ratio, "min": minimum,
                     "usage": usage, "pass": ratio + 1e-9 >= minimum})
    return rows


def validate(tokens: dict) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block saving/applying a system."""
    errors: list[str] = []
    warnings: list[str] = []
    info = L.meta(tokens)
    level = (info.get("spec") or {}).get("contrast", "AA")

    for key in ("id", "name"):
        if not info.get(key):
            errors.append(f"$extensions.designku.{key} is missing")

    # ---- structure
    for mode in ("light", "dark"):
        for role in REQUIRED_ROLES:
            try:
                value = L.tv(tokens, f"color.{mode}.{role}")
                L.hex_to_rgb(value)
            except KeyError:
                errors.append(f"color.{mode}.{role} is missing or has a broken alias")
            except (ValueError, TypeError, AttributeError):
                errors.append(f"color.{mode}.{role} is not a hex color")
    try:
        light_keys, dark_keys = set(tokens["color"]["light"]), set(tokens["color"]["dark"])
        for extra in sorted(light_keys ^ dark_keys):
            errors.append(f"color role '{extra}' exists in only one of light/dark")
    except KeyError:
        errors.append("color.light / color.dark group is missing")

    for group, names in REQUIRED_GROUPS.items():
        for name in names:
            try:
                L.tv(tokens, f"{group}.{name}")
            except KeyError:
                errors.append(f"{group}.{name} is missing or has a broken alias")
    for role in REQUIRED_TYPE:
        try:
            style = L.tv(tokens, f"typography.scale.{role}")
            size = L.num(style["fontSize"])
            if size < 11:
                errors.append(f"typography.scale.{role} is {size:g}px — below the 11px legibility floor")
            if role.startswith("body") and float(style["lineHeight"]) < 1.3:
                errors.append(f"typography.scale.{role} line height {style['lineHeight']} < 1.3 (WCAG 1.4.12 text spacing)")
            if not isinstance(style["fontFamily"], list) or len(style["fontFamily"]) < 2:
                errors.append(f"typography.scale.{role} needs a font family with at least one fallback")
        except (KeyError, TypeError, ValueError):
            errors.append(f"typography.scale.{role} is missing or malformed")
    if errors:
        return errors, warnings

    if L.num(L.tv(tokens, "typography.scale.bodyMedium")["fontSize"]) < 14:
        errors.append("typography.scale.bodyMedium must be >= 14px for mobile body text")
    for name, value in L.group_items(tokens, "spacing"):
        px = L.num(value)
        if px % 4 != 0 and name != "xxs":
            errors.append(f"spacing.{name} = {px:g}px is off the 4pt grid")
    if L.num(L.tv(tokens, "size.touchTarget")) < 48:
        errors.append("size.touchTarget must be >= 48px")
    if L.num(L.tv(tokens, "size.input")) < 48 or L.num(L.tv(tokens, "size.listItem")) < 48:
        errors.append("size.input and size.listItem must be >= 48px (touch target)")
    for name, value in L.group_items(tokens, "motion.duration"):
        if L.num(value) > 1000:
            warnings.append(f"motion.duration.{name} > 1000ms feels sluggish on mobile")

    # ---- contrast (the core guarantee)
    for mode in ("light", "dark"):
        for row in measure(tokens, mode, level):
            if not row["pass"]:
                errors.append(
                    f"[{mode}] {row['fg']} {row['fgHex']} on {row['bg']} {row['bgHex']} = "
                    f"{row['ratio']:.2f}:1, needs {row['min']:g}:1 ({row['usage']})")

    # ---- perceptual sanity
    cvd: list[str] = []
    for mode in ("light", "dark"):
        c = {role: L.tv(tokens, f"color.{mode}.{role}") for role in REQUIRED_ROLES}
        d_pe = L.delta_e_ok(c["primary"], c["error"])
        hue_gap = L.hue_distance(L.hex_to_oklch(c["primary"])[2], L.hex_to_oklch(c["error"])[2])
        if d_pe < 0.05 or (d_pe < 0.10 and hue_gap < 30):
            errors.append(f"[{mode}] error {c['error']} is too close to primary {c['primary']} "
                          f"(ΔE_OK {d_pe:.3f}, hue gap {hue_gap:.0f}°) — destructive actions would look like the main CTA")
        statuses = ["error", "success", "warning", "info"]
        for kind in L.CVD_MATRICES:
            for i, a in enumerate(statuses):
                for b in statuses[i + 1:]:
                    d = L.delta_e_ok(L.simulate_cvd(c[a], kind), L.simulate_cvd(c[b], kind))
                    if d < 0.045:
                        cvd.append(f"{a}/{b} ({kind}, {mode})")
        if mode == "dark":
            if c["surface"].upper() == "#000000":
                warnings.append("[dark] surface is pure #000000 — causes OLED smearing and halation; prefer a tinted near-black")
            if c["onSurface"].upper() == "#FFFFFF":
                warnings.append("[dark] onSurface is pure #FFFFFF — prefer a slightly dimmed tone to reduce glare")
            if L.contrast(c["surface"], c["surfaceContainerHigh"]) < 1.08:
                warnings.append("[dark] surface and surfaceContainerHigh are barely distinguishable — elevation will not read")
    if cvd:
        warnings.append(f"color-blind check: {len(cvd)} status pair(s) collapse under simulation, e.g. {', '.join(cvd[:3])} — "
                        "expected for equal-tone status colors; status must always carry an icon and a text label")
    fonts = info.get("fonts") or {}
    for slot, family in fonts.items():
        if family not in L.FONTS:
            warnings.append(f"font '{family}' ({slot}) is not in the curated Google Fonts list — verify it exists and is OFL")
    return errors, _dedupe(warnings)


def _dedupe(items: list[str]) -> list[str]:
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def summary(tokens: dict) -> dict:
    """Smallest measured ratio per mode, for reports."""
    level = (L.meta(tokens).get("spec") or {}).get("contrast", "AA")
    out = {}
    for mode in ("light", "dark"):
        rows = measure(tokens, mode, level)
        text = [r["ratio"] for r in rows if r["min"] >= 4.5]
        ui = [r["ratio"] for r in rows if r["min"] < 4.5]
        out[mode] = {"pairs": len(rows), "minText": min(text), "minUi": min(ui)}
    return out
