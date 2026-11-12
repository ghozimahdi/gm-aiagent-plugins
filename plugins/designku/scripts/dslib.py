#!/usr/bin/env python3
"""designku shared library: color math, DTCG token helpers, system discovery.

Pure python3 stdlib. Imported by every other designku script.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
BUILTIN_DIR = PLUGIN_ROOT / "systems"
SCHEMA_VERSION = 1
PROJECT_DIR_NAME = ".designku"

# --------------------------------------------------------------------------- paths


def user_home() -> Path:
    """User-level designku home (custom systems, catalog). Override: DESIGNKU_HOME."""
    override = os.environ.get("DESIGNKU_HOME")
    return Path(override).expanduser() if override else Path.home() / ".designku"


def custom_dir() -> Path:
    return user_home() / "systems"


def file_url(path: Path) -> str:
    return Path(path).resolve().as_uri()


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from `start` looking for .designku/config.json."""
    cur = Path(start or Path.cwd()).resolve()
    if cur.is_file():
        cur = cur.parent
    for candidate in [cur, *cur.parents]:
        if (candidate / PROJECT_DIR_NAME / "config.json").is_file():
            return candidate
    return None


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "system"


# --------------------------------------------------------------------------- color math


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) == 8:  # RRGGBBAA -> drop alpha
        h = h[:6]
    if len(h) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"invalid hex color: {value!r}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def _to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _to_gamma(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def luminance(value: str) -> float:
    r, g, b = (_to_linear(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def linear_to_oklab(r: float, g: float, b: float):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = _cbrt(l), _cbrt(m), _cbrt(s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear(L: float, a: float, b: float):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def hex_to_oklab(value: str):
    return linear_to_oklab(*(_to_linear(c) for c in hex_to_rgb(value)))


def hex_to_oklch(value: str):
    L, a, b = hex_to_oklab(value)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def _oklch_to_linear(L: float, C: float, h: float):
    rad = math.radians(h)
    return oklab_to_linear(L, C * math.cos(rad), C * math.sin(rad))


def _in_gamut(rgb, eps: float = 1e-4) -> bool:
    return all(-eps <= c <= 1 + eps for c in rgb)


def _fit_chroma(L: float, C: float, h: float):
    """Largest chroma <= C that is inside sRGB for this lightness/hue."""
    rgb = _oklch_to_linear(L, C, h)
    if _in_gamut(rgb):
        return rgb
    lo, hi = 0.0, C
    for _ in range(22):
        mid = (lo + hi) / 2
        if _in_gamut(_oklch_to_linear(L, mid, h)):
            lo = mid
        else:
            hi = mid
    return _oklch_to_linear(L, lo, h)


def tone_to_y(tone: float) -> float:
    """CIE L* (0-100) -> relative luminance Y."""
    return ((tone + 16) / 116) ** 3 if tone > 8 else tone / 903.3


def y_to_tone(y: float) -> float:
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else y * 903.3


def tone_of(value: str) -> float:
    return y_to_tone(luminance(value))


def tonal_color(hue: float, chroma: float, tone: float) -> str:
    """HCT-like tonal step: OKLCH hue/chroma, CIE L* lightness (`tone`).

    Because the lightness axis is L*, a fixed tone gap gives a predictable WCAG
    contrast ratio (gap >= 50 -> >= 4.5:1, gap >= 40 -> >= 3:1) whatever the hue.
    """
    if tone <= 0:
        return "#000000"
    if tone >= 100:
        return "#FFFFFF"
    target = tone_to_y(tone)
    lo, hi = 0.0, 1.0
    rgb = (0.0, 0.0, 0.0)
    for _ in range(30):
        mid = (lo + hi) / 2
        rgb = _fit_chroma(mid, chroma, hue)
        y = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        if y < target:
            lo = mid
        else:
            hi = mid
    return rgb_to_hex(tuple(_to_gamma(max(0.0, min(1.0, c))) for c in rgb))


def delta_e_ok(a: str, b: str) -> float:
    la, lb = hex_to_oklab(a), hex_to_oklab(b)
    return math.dist(la, lb)


def hue_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


# Machado, Oliveira & Fernandes (2009), severity 1.0, applied in linear RGB.
CVD_MATRICES = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def simulate_cvd(value: str, kind: str) -> str:
    lin = [_to_linear(c) for c in hex_to_rgb(value)]
    out = [sum(row[i] * lin[i] for i in range(3)) for row in CVD_MATRICES[kind]]
    return rgb_to_hex(tuple(_to_gamma(max(0.0, min(1.0, c))) for c in out))


def with_alpha(value: str, alpha: float) -> str:
    return value[:7].upper() + f"{max(0, min(255, round(alpha * 255))):02X}"


# --------------------------------------------------------------------------- DTCG helpers

_ALIAS = re.compile(r"^\{([^{}]+)\}$")


def get_path(tokens: dict, path: str):
    node = tokens
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def resolve(tokens: dict, value, _depth: int = 0):
    """Resolve DTCG aliases ("{group.token}") recursively, including inside composites."""
    if _depth > 20:
        raise ValueError("alias cycle")
    if isinstance(value, str):
        match = _ALIAS.match(value)
        if match:
            target = get_path(tokens, match.group(1))
            if isinstance(target, dict) and "$value" in target:
                target = target["$value"]
            return resolve(tokens, target, _depth + 1)
        return value
    if isinstance(value, dict):
        return {k: resolve(tokens, v, _depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(tokens, v, _depth + 1) for v in value]
    return value


def tv(tokens: dict, path: str):
    """Resolved $value of the token at `path`."""
    return resolve(tokens, get_path(tokens, path)["$value"])


def alias_of(tokens: dict, path: str) -> str | None:
    raw = get_path(tokens, path)["$value"]
    if isinstance(raw, str):
        match = _ALIAS.match(raw)
        if match:
            return match.group(1)
    return None


def num(value) -> float:
    """Number out of a DTCG dimension/duration ({"value": 16, "unit": "px"}) or raw number."""
    if isinstance(value, dict) and "value" in value:
        return float(value["value"])
    if isinstance(value, (int, float)):
        return float(value)
    match = re.match(r"^-?\d+(\.\d+)?", str(value))
    if not match:
        raise ValueError(f"not a number: {value!r}")
    return float(match.group(0))


def group_items(tokens: dict, path: str) -> list[tuple[str, object]]:
    """(name, resolved value) for every token directly inside a group."""
    group = get_path(tokens, path)
    return [(k, resolve(tokens, v["$value"])) for k, v in group.items() if isinstance(v, dict) and "$value" in v]


def meta(tokens: dict) -> dict:
    return tokens.get("$extensions", {}).get("designku", {})


def fmt_num(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


# --------------------------------------------------------------------------- fonts

# Curated free Google Fonts (OFL unless noted). kind: sans | serif | rounded | mono.
FONTS = {
    "Inter": ("sans", "Neutral UI workhorse, tall x-height"),
    "Manrope": ("sans", "Geometric, confident, good numerals"),
    "Public Sans": ("sans", "Plain, institutional, very legible"),
    "Plus Jakarta Sans": ("sans", "Friendly geometric, retail-ready"),
    "Jost": ("sans", "Geometric, Futura-like poster headlines"),
    "Mulish": ("sans", "Minimal sans, very legible at small UI sizes"),
    "DM Sans": ("sans", "Low-contrast geometric, warm"),
    "Figtree": ("sans", "Clean and gentle, open shapes"),
    "Outfit": ("sans", "Soft geometric headlines"),
    "Sora": ("sans", "Wide, techy, energetic"),
    "Be Vietnam Pro": ("sans", "Contemporary humanist"),
    "IBM Plex Sans": ("sans", "Engineered, enterprise tone"),
    "Source Sans 3": ("sans", "Classic humanist UI face"),
    "Work Sans": ("sans", "Grotesque, relaxed"),
    "Poppins": ("sans", "Geometric, round, popular"),
    "Urbanist": ("sans", "Modern low-contrast geometric"),
    "Space Grotesk": ("sans", "Quirky grotesque, tech"),
    "Lexend": ("sans", "Designed for reading proficiency"),
    "Atkinson Hyperlegible": ("sans", "Maximum character distinction (low vision)"),
    "Roboto": ("sans", "Android default (Apache-2.0)"),
    "Nunito": ("rounded", "Rounded terminals, friendly"),
    "Nunito Sans": ("sans", "Nunito without the rounding"),
    "Quicksand": ("rounded", "Light rounded display"),
    "Rubik": ("rounded", "Slightly rounded corners"),
    "Baloo 2": ("rounded", "Chunky, playful headlines"),
    "Fredoka": ("rounded", "Bold rounded, kids"),
    "Fraunces": ("serif", "Soft old-style serif with character"),
    "Lora": ("serif", "Calligraphic text serif"),
    "Merriweather": ("serif", "Sturdy screen serif"),
    "Playfair Display": ("serif", "High-contrast editorial serif"),
    "Source Serif 4": ("serif", "Transitional reading serif"),
    "JetBrains Mono": ("mono", "Code and tabular data"),
    "IBM Plex Mono": ("mono", "Engineered mono"),
    "Roboto Mono": ("mono", "Neutral mono (Apache-2.0)"),
}

FALLBACKS = {
    "sans": ["system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
    "rounded": ["ui-rounded", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
    "serif": ["ui-serif", "Georgia", "Times New Roman", "serif"],
    "mono": ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
}


def font_stack(family: str, default_kind: str = "sans") -> list[str]:
    kind = FONTS.get(family, (default_kind, ""))[0]
    return [family, *FALLBACKS[kind]]


def google_fonts_url(families: list[str]) -> str:
    seen, parts = set(), []
    for fam in families:
        if fam in seen:
            continue
        seen.add(fam)
        parts.append("family=" + fam.replace(" ", "+") + ":wght@400;500;600;700")
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


# --------------------------------------------------------------------------- systems

GROUPS = {
    "business": "Trust & Work",
    "commerce": "Commerce & Lifestyle",
    "wellbeing": "Care & Learning",
    "custom": "My custom systems",
}


def _load_system(directory: Path, source: str) -> dict | None:
    tokens_path = directory / "tokens.json"
    if not tokens_path.is_file():
        return None
    try:
        tokens = read_json(tokens_path)
    except (OSError, ValueError):
        return None
    info = meta(tokens)
    return {
        "id": info.get("id") or directory.name,
        "name": info.get("name") or directory.name,
        "letter": info.get("letter", ""),
        "context": info.get("context", ""),
        "group": info.get("group", "custom") if source == "builtin" else "custom",
        "tagline": info.get("tagline", ""),
        "source": source,
        "dir": directory,
        "tokens_path": tokens_path,
        "tokens": tokens,
        "mtime": tokens_path.stat().st_mtime,
    }


def list_systems() -> list[dict]:
    """Built-in systems (plugin) followed by custom systems (~/.designku/systems)."""
    out: list[dict] = []
    if BUILTIN_DIR.is_dir():
        builtins = [s for s in (_load_system(d, "builtin") for d in sorted(BUILTIN_DIR.iterdir()) if d.is_dir()) if s]
        out.extend(sorted(builtins, key=lambda s: (s["letter"] or "Z", s["id"])))
    cdir = custom_dir()
    if cdir.is_dir():
        customs = [s for s in (_load_system(d, "custom") for d in sorted(cdir.iterdir()) if d.is_dir()) if s]
        out.extend(sorted(customs, key=lambda s: -s["mtime"]))
    return out


def find_system(ref: str) -> dict | None:
    """Look up by id, single letter (A-H) or `custom:<id>` / `builtin:<id>`."""
    ref = ref.strip()
    want_source = None
    if ":" in ref:
        want_source, ref = ref.split(":", 1)
    systems = list_systems()
    key = ref.lower()
    for system in systems:
        if want_source and system["source"] != want_source:
            continue
        if system["id"].lower() == key:
            return system
    for system in systems:
        if want_source and system["source"] != want_source:
            continue
        if system["letter"] and system["letter"].lower() == key:
            return system
        if system["name"].lower() == key:
            return system
    return None


def system_ids() -> set[str]:
    return {s["id"] for s in list_systems()}
