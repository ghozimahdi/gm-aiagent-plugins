#!/usr/bin/env python3
"""designku token engine: compact spec -> full W3C DTCG tokens.json.

The same engine builds the built-in catalog (ds_builtins.py) and every custom
system (ds_derive.py), so all systems share one structure and one set of
accessibility guarantees. Platform-agnostic: nothing here knows about Flutter.
"""
from __future__ import annotations

import copy

import dslib as L

CHROMATIC_TONES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100]
NEUTRAL_TONES = [0, 2, 4, 6, 10, 12, 17, 20, 22, 24, 30, 40, 50, 60, 70, 80, 87, 90, 92, 94, 95, 96, 98, 99, 100]
FAMILIES = ["primary", "secondary", "tertiary", "error", "success", "warning", "info"]

DEFAULT_SPEC = {
    "primary": "#3F51B5",
    "secondary": None,  # derived from primary + mood when null
    "tertiary": None,
    "neutralHue": None,  # degrees (OKLCH); defaults to the primary hue
    "neutralChroma": 0.006,
    "error": "#BA1A1A",
    "success": "#1E8E3E",
    "warning": "#B26A00",
    "info": "#0B6BCB",
    "mood": "balanced",  # calm | balanced | vibrant | professional | warm | playful
    "fonts": {"display": "Inter", "body": "Inter", "mono": "JetBrains Mono"},
    "type": {"displayWeight": 600, "headlineWeight": 600, "titleWeight": 600, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -0.5},
    "corner": "soft",  # sharp | soft | rounded | pill
    "density": "comfortable",  # compact | comfortable | spacious
    "motion": "balanced",  # snappy | balanced | expressive
    "elevation": "soft",  # flat | soft | lifted
    "darkStyle": "tinted",  # tinted | oled
    "contrast": "AA",  # AA | AAA
    "tones": {"light": {}, "dark": {}},  # role -> tone override, e.g. {"light": {"primary": 45}}
    "overrides": {"light": {}, "dark": {}},  # role -> exact hex, for systems ported from an existing brand
    "style": "material",  # material | brutal (neo-brutalism: ink stroke + hard offset shadow)
}

# style -> (stroke width px, hard shadow offset px, hard shadow in dark mode)
STYLES = {
    "material": (0, 0, False),
    "brutal": (1.5, 3, False),
}

# mood -> (secondary chroma factor, tertiary hue shift, tertiary chroma factor, neutral chroma)
MOODS = {
    "calm": (0.30, 40, 0.45, 0.008),
    "balanced": (0.35, 60, 0.60, 0.006),
    "vibrant": (0.55, 120, 0.90, 0.006),
    "professional": (0.22, 30, 0.40, 0.004),
    "warm": (0.40, -40, 0.70, 0.012),
    "playful": (0.60, 150, 0.95, 0.010),
}

CORNERS = {
    #           xs  sm  md  lg  xl   button  input  card  chip    dialog sheet
    "sharp": ((2, 4, 6, 8, 12), "sm", "sm", "md", "sm", "lg", "lg"),
    "soft": ((4, 8, 12, 16, 24), "md", "md", "lg", "sm", "xl", "xl"),
    "rounded": ((6, 12, 16, 24, 32), "md", "md", "lg", "full", "xl", "xl"),
    "pill": ((8, 12, 20, 28, 36), "full", "lg", "lg", "full", "xl", "xl"),
}

DENSITIES = {
    #               btnSm btnMd btnLg input listItem appBar navBar
    "compact": (32, 40, 48, 48, 56, 56, 64),
    "comfortable": (36, 48, 56, 56, 64, 64, 72),
    "spacious": (40, 52, 60, 60, 72, 64, 80),
}

MOTIONS = {
    "snappy": (0.8, [0.2, 0.0, 0.0, 1.0], [0.3, 0.0, 0.0, 1.0]),
    "balanced": (1.0, [0.2, 0.0, 0.0, 1.0], [0.2, 0.0, 0.0, 1.0]),
    "expressive": (1.2, [0.2, 0.0, 0.0, 1.0], [0.34, 1.36, 0.64, 1.0]),
}

ELEVATIONS = {"flat": 0.55, "soft": 1.0, "lifted": 1.45}

# M3 type scale: role -> (size, line height px, tracking px, family slot, weight slot)
TYPE_SCALE = [
    ("displayLarge", 57, 64, None, "display", "displayWeight"),
    ("displayMedium", 45, 52, None, "display", "displayWeight"),
    ("displaySmall", 36, 44, None, "display", "displayWeight"),
    ("headlineLarge", 32, 40, None, "display", "headlineWeight"),
    ("headlineMedium", 28, 36, None, "display", "headlineWeight"),
    ("headlineSmall", 24, 32, None, "display", "headlineWeight"),
    ("titleLarge", 22, 28, 0, "display", "titleWeight"),
    ("titleMedium", 16, 24, 0.1, "body", "titleWeight"),
    ("titleSmall", 14, 20, 0.1, "body", "titleWeight"),
    ("bodyLarge", 16, 24, 0.15, "body", "bodyWeight"),
    ("bodyMedium", 14, 20, 0.1, "body", "bodyWeight"),
    ("bodySmall", 12, 16, 0.2, "body", "bodyWeight"),
    ("labelLarge", 14, 20, 0.1, "body", "labelWeight"),
    ("labelMedium", 12, 16, 0.3, "body", "labelWeight"),
    ("labelSmall", 11, 16, 0.3, "body", "labelWeight"),
]


def merge_spec(base: dict, override: dict | None) -> dict:
    """Deep-merge `override` on top of `base` (None values in override are ignored)."""
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if value is None:
            continue
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merge_spec(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _px(value: float) -> dict:
    return {"value": value, "unit": "px"}


def _ms(value: float) -> dict:
    return {"value": int(round(value)), "unit": "ms"}


def _tok(kind: str, value, description: str | None = None) -> dict:
    token = {"$type": kind, "$value": value}
    if description:
        token["$description"] = description
    return token


def _seed_hc(spec: dict) -> dict[str, tuple[float, float]]:
    """(hue, chroma) per palette. Secondary/tertiary are derived when not given."""
    _, p_c, p_h = L.hex_to_oklch(spec["primary"])
    sec_f, ter_shift, ter_f, mood_neutral = MOODS.get(spec.get("mood", "balanced"), MOODS["balanced"])
    hc: dict[str, tuple[float, float]] = {"primary": (p_h, p_c)}
    if spec.get("secondary"):
        _, c, h = L.hex_to_oklch(spec["secondary"])
        hc["secondary"] = (h, c)
    else:
        hc["secondary"] = (p_h, max(0.02, p_c * sec_f))
    if spec.get("tertiary"):
        _, c, h = L.hex_to_oklch(spec["tertiary"])
        hc["tertiary"] = (h, c)
    else:
        hc["tertiary"] = ((p_h + ter_shift) % 360, max(0.04, p_c * ter_f))
    for fam in ("error", "success", "warning", "info"):
        _, c, h = L.hex_to_oklch(spec[fam])
        hc[fam] = (h, c)
    n_h = spec["neutralHue"] if spec.get("neutralHue") is not None else p_h
    n_c = spec["neutralChroma"] if spec.get("neutralChroma") is not None else mood_neutral
    hc["neutral"] = (n_h, n_c)
    hc["neutralVariant"] = (n_h, min(0.04, n_c * 2.2 + 0.004))
    return hc


def _chroma_taper(tone: int) -> float:
    """Desaturate the light end of chromatic ramps.

    Container fills (tone 90+) at full seed chroma turn neon (mint-green success
    badges, candy-pink errors) and fight the brand color. Tapering keeps them as
    quiet tints; contrast is unaffected because it depends on tone only.
    """
    if tone >= 95:
        return 0.35
    if tone >= 90:
        return 0.45
    if tone >= 80:
        return 0.80
    return 1.0


class _Palette:
    def __init__(self, hc: dict[str, tuple[float, float]]):
        self.hc = hc
        self.tones: dict[str, dict[int, str]] = {name: {} for name in hc}

    def ensure(self, name: str, tone: int) -> str:
        tone = int(tone)
        if tone not in self.tones[name]:
            hue, chroma = self.hc[name]
            if name in FAMILIES:
                chroma *= _chroma_taper(tone)
            self.tones[name][tone] = L.tonal_color(hue, chroma, tone)
        return self.tones[name][tone]

    def ref(self, name: str, tone: int) -> str:
        self.ensure(name, tone)
        return "{color.palette.%s.%d}" % (name, int(tone))


def _auto_on(pal: _Palette, fam: str, bg_tone: int, target: float) -> int:
    """Pick the on-color tone for a filled surface of `fam` at `bg_tone`."""
    bg = pal.ensure(fam, bg_tone)
    prefs = [20, 10, 0] if bg_tone >= 50 else [100]
    for tone in prefs:
        if L.contrast(pal.ensure(fam, tone), bg) >= target:
            return tone
    return max([100, 20, 10, 0], key=lambda t: L.contrast(pal.ensure(fam, t), bg))


def _semantic(spec: dict, pal: _Palette, mode: str) -> dict:
    light = mode == "light"
    aaa = spec.get("contrast") == "AAA"
    target = 7.0 if aaa else 4.5
    over = (spec.get("tones") or {}).get(mode, {}) or {}
    out: dict[str, dict] = {}

    def put(role: str, palette: str, tone: int, desc: str | None = None):
        tone = int(over.get(role, tone))
        out[role] = _tok("color", pal.ref(palette, tone), desc)
        return tone

    for fam in FAMILIES:
        cap = fam[0].upper() + fam[1:]
        base = (30 if aaa else 40) if light else 80
        tone = put(fam, fam, base, f"{cap} fills and {fam}-colored text/icons on surfaces")
        on_tone = int(over.get("on" + cap, _auto_on(pal, fam, tone, target)))
        out["on" + cap] = _tok("color", pal.ref(fam, on_tone), f"Text/icons on {fam}")
        put(fam + "Container", fam, 90 if light else 30, f"Low-emphasis {fam} fill")
        put("on" + cap + "Container", fam, 10 if light else 90, f"Text/icons on {fam}Container")

    oled = spec.get("darkStyle") == "oled"
    if light:
        surf = [("background", 98), ("surface", 98), ("surfaceDim", 87), ("surfaceBright", 98),
                ("surfaceContainerLowest", 100), ("surfaceContainerLow", 96), ("surfaceContainer", 94),
                ("surfaceContainerHigh", 92), ("surfaceContainerHighest", 90),
                ("onBackground", 10), ("onSurface", 10), ("inverseSurface", 20), ("onInverseSurface", 95),
                ("scrim", 0), ("shadow", 0)]
        variant = [("surfaceVariant", 90), ("onSurfaceVariant", 20 if aaa else 30),
                   ("outline", 40 if aaa else 50), ("outlineVariant", 80)]
    else:
        if oled:
            steps = (4, 4, 4, 22, 2, 6, 10, 12, 17)
        else:
            steps = (6, 6, 6, 24, 4, 10, 12, 17, 22)
        names = ("background", "surface", "surfaceDim", "surfaceBright", "surfaceContainerLowest",
                 "surfaceContainerLow", "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest")
        surf = list(zip(names, steps)) + [("onBackground", 90), ("onSurface", 90), ("inverseSurface", 90),
                                         ("onInverseSurface", 20), ("scrim", 0), ("shadow", 0)]
        variant = [("surfaceVariant", 30), ("onSurfaceVariant", 90 if aaa else 80), ("outline", 60), ("outlineVariant", 30)]
    for role, tone in surf:
        put(role, "neutral", tone)
    for role, tone in variant:
        put(role, "neutralVariant", tone)
    # inversePrimary sits on inverseSurface (snackbar action): mirror the other mode's primary.
    other = "dark" if light else "light"
    other_over = (spec.get("tones") or {}).get(other, {}) or {}
    inv_default = 80 if light else (30 if aaa else 40)
    inv_tone = int(other_over.get("primary", inv_default))
    inv_surface = pal.ensure("neutral", 20 if light else 90)
    if L.contrast(pal.ensure("primary", inv_tone), inv_surface) < target:
        inv_tone = inv_default  # the mirrored tone is too weak on inverseSurface
    put("inversePrimary", "primary", inv_tone)
    out["surfaceTint"] = _tok("color", "{color.%s.primary}" % mode, "Elevation tint")
    for role, hex_value in ((spec.get("overrides") or {}).get(mode) or {}).items():
        if role not in out:
            raise ValueError(f"overrides.{mode}.{role}: unknown color role")
        out[role] = _tok("color", L.rgb_to_hex(L.hex_to_rgb(hex_value)), out[role].get("$description"))
    return out


def build_tokens(meta: dict, spec_in: dict) -> dict:
    """Build a complete DTCG token tree. `meta` = identity/rationale, `spec_in` = generator spec."""
    spec = merge_spec(DEFAULT_SPEC, spec_in)
    hc = _seed_hc(spec)
    pal = _Palette(hc)
    for name in hc:
        steps = NEUTRAL_TONES if name == "neutral" else CHROMATIC_TONES
        for tone in steps:
            pal.ensure(name, tone)

    light = _semantic(spec, pal, "light")
    dark = _semantic(spec, pal, "dark")

    palette = {
        name: {str(t): _tok("color", pal.tones[name][t]) for t in sorted(pal.tones[name])}
        for name in pal.tones
    }

    # ---- typography
    fonts = spec["fonts"]
    weights = spec["type"]
    families = {
        "display": _tok("fontFamily", L.font_stack(fonts["display"]), "Display, headline and large title"),
        "body": _tok("fontFamily", L.font_stack(fonts["body"]), "Body, label and small title"),
        "mono": _tok("fontFamily", L.font_stack(fonts.get("mono") or "JetBrains Mono", "mono"), "Code and tabular numbers"),
    }
    scale = {}
    for role, size, line, tracking, slot, weight_slot in TYPE_SCALE:
        if tracking is None:  # display + headline share the configurable optical tracking
            tracking = round(weights.get("displayTracking", -0.5) * (size / 57), 2)
        scale[role] = _tok("typography", {
            "fontFamily": "{typography.fontFamily.%s}" % slot,
            "fontSize": _px(size),
            "fontWeight": int(weights[weight_slot]),
            "lineHeight": round(line / size, 3),
            "letterSpacing": _px(tracking),
        })

    # ---- shape
    (r_xs, r_sm, r_md, r_lg, r_xl), s_btn, s_in, s_card, s_chip, s_dlg, s_sheet = CORNERS[spec["corner"]]
    radius = {
        "none": _tok("dimension", _px(0)),
        "xs": _tok("dimension", _px(r_xs)),
        "sm": _tok("dimension", _px(r_sm)),
        "md": _tok("dimension", _px(r_md)),
        "lg": _tok("dimension", _px(r_lg)),
        "xl": _tok("dimension", _px(r_xl)),
        "full": _tok("dimension", _px(999), "Pill / circle"),
    }
    shape = {
        name: _tok("dimension", "{radius.%s}" % ref)
        for name, ref in (("button", s_btn), ("input", s_in), ("card", s_card), ("chip", s_chip),
                          ("dialog", s_dlg), ("sheet", s_sheet))
    }

    # ---- size (density)
    b_sm, b_md, b_lg, inp, item, app_bar, nav_bar = DENSITIES[spec["density"]]
    size = {
        "touchTarget": _tok("dimension", _px(48), "Minimum interactive target (WCAG 2.5.8 / Material)"),
        "buttonSm": _tok("dimension", _px(b_sm), "Visual height; tap area is still padded to touchTarget"),
        "buttonMd": _tok("dimension", _px(b_md)),
        "buttonLg": _tok("dimension", _px(b_lg)),
        "input": _tok("dimension", _px(inp)),
        "listItem": _tok("dimension", _px(item)),
        "appBar": _tok("dimension", _px(app_bar)),
        "navBar": _tok("dimension", _px(nav_bar)),
        "avatarSm": _tok("dimension", _px(32)),
        "avatarMd": _tok("dimension", _px(40)),
        "avatarLg": _tok("dimension", _px(64)),
    }

    # ---- elevation
    strength = ELEVATIONS[spec["elevation"]]
    shadow_base = pal.ensure("neutral", 10)
    layers = [
        [],
        [(0, 1, 2, 0, 0.10), (0, 1, 3, 1, 0.06)],
        [(0, 1, 2, 0, 0.10), (0, 2, 6, 2, 0.07)],
        [(0, 1, 3, 0, 0.10), (0, 4, 8, 3, 0.08)],
        [(0, 2, 3, 0, 0.10), (0, 6, 10, 4, 0.08)],
        [(0, 4, 4, 0, 0.10), (0, 8, 12, 6, 0.08)],
    ]
    dps = [0, 1, 3, 6, 8, 12]
    elevation = {}
    for index, parts in enumerate(layers):
        token = _tok("shadow", [
            {"color": L.with_alpha(shadow_base, min(0.6, alpha * strength)), "offsetX": _px(x), "offsetY": _px(y),
             "blur": _px(blur), "spread": _px(spread)}
            for (x, y, blur, spread, alpha) in parts
        ])
        token["$extensions"] = {"designku": {"dp": dps[index]}}
        elevation[f"level{index}"] = token

    # ---- motion
    factor, standard, emphasized = MOTIONS[spec["motion"]]
    motion = {
        "duration": {
            "instant": _tok("duration", _ms(0)),
            "fast": _tok("duration", _ms(100 * factor), "Micro feedback: ripple, toggle"),
            "normal": _tok("duration", _ms(200 * factor), "Most transitions"),
            "slow": _tok("duration", _ms(300 * factor), "Sheets, dialogs, page elements"),
            "slower": _tok("duration", _ms(500 * factor), "Full-screen transitions"),
        },
        "easing": {
            "standard": _tok("cubicBezier", standard),
            "emphasized": _tok("cubicBezier", emphasized),
            "decelerate": _tok("cubicBezier", [0.0, 0.0, 0.0, 1.0], "Entering elements"),
            "accelerate": _tok("cubicBezier", [0.3, 0.0, 1.0, 1.0], "Exiting elements"),
        },
    }

    # ---- surface style (material = shadows only; brutal = ink stroke + hard offset shadow)
    style = spec.get("style", "material")
    if style not in STYLES:
        raise ValueError(f"unknown style '{style}' (use one of {', '.join(STYLES)})")
    stroke, offset, in_dark = STYLES[style]
    effect = {
        "style": _tok("string", style, "material | brutal"),
        "strokeWidth": _tok("dimension", _px(stroke), "Ink outline on primary actions and raised surfaces (0 = none)"),
        "shadowOffset": _tok("dimension", _px(offset), "Hard shadow x/y offset, zero blur, color onSurface (0 = none)"),
        "shadowInDark": _tok("boolean", in_dark, "Hard shadow also drawn in dark mode"),
    }

    info = copy.deepcopy(meta)
    info["schemaVersion"] = L.SCHEMA_VERSION
    info["spec"] = spec
    info["fonts"] = {"display": fonts["display"], "body": fonts["body"], "mono": fonts.get("mono") or "JetBrains Mono"}

    return {
        "$description": f"{info.get('name', info.get('id', 'designku'))} design system tokens (W3C DTCG format). "
                        "Single source of truth: edit here, then regenerate platform code.",
        "$extensions": {"designku": info},
        "color": {"palette": palette, "light": light, "dark": dark},
        "typography": {"fontFamily": families, "scale": scale},
        "spacing": {
            "none": _tok("dimension", _px(0)),
            "xxs": _tok("dimension", _px(2), "Hairline gaps only (icon-to-badge)"),
            "xs": _tok("dimension", _px(4)),
            "sm": _tok("dimension", _px(8)),
            "md": _tok("dimension", _px(12)),
            "lg": _tok("dimension", _px(16), "Default screen gutter"),
            "xl": _tok("dimension", _px(24)),
            "xxl": _tok("dimension", _px(32)),
            "xxxl": _tok("dimension", _px(48)),
            "huge": _tok("dimension", _px(64)),
        },
        "radius": radius,
        "shape": shape,
        "borderWidth": {
            "none": _tok("dimension", _px(0)),
            "thin": _tok("dimension", _px(1), "Dividers, outlined components"),
            "thick": _tok("dimension", _px(2), "Focused input, selected state"),
            "focus": _tok("dimension", _px(3), "Keyboard focus ring"),
        },
        "elevation": elevation,
        "effect": effect,
        "motion": motion,
        "iconSize": {
            "xs": _tok("dimension", _px(16)),
            "sm": _tok("dimension", _px(20)),
            "md": _tok("dimension", _px(24), "Default"),
            "lg": _tok("dimension", _px(32)),
            "xl": _tok("dimension", _px(48)),
        },
        "size": size,
        "opacity": {
            "disabled": _tok("number", 0.38, "Disabled content"),
            "disabledContainer": _tok("number", 0.12, "Disabled fill"),
            "hover": _tok("number", 0.08),
            "focus": _tok("number", 0.10),
            "pressed": _tok("number", 0.10),
            "scrim": _tok("number", 0.32),
        },
    }
