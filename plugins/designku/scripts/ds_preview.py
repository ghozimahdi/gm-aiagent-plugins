#!/usr/bin/env python3
"""designku preview renderer: tokens.json -> one self-contained preview.html.

Pure python3 stdlib. The only external request in the output is the Google
Fonts stylesheet; all CSS, JS and icons are inline. Everything on the page is
styled exclusively through CSS variables generated from the tokens, so the
preview is an honest picture of the system.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import dslib as L
import ds_validate

RENDERER_VERSION = "2"

ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "bell": '<path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 7H4c0-1 2-2 2-7z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "chevron-right": '<path d="M9 6l6 6-6 6"/>',
    "chevron-down": '<path d="M6 9l6 6 6-6"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "more": '<circle cx="12" cy="5" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="12" cy="19" r="1.2"/>',
    "sliders": '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "star": '<path d="M12 3l2.8 5.8 6.2.8-4.5 4.4 1.1 6.3L12 17.3l-5.6 3 1.1-6.3L3 9.6l6.2-.8z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "alert": '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="M21 16l-5-5-8 8"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
    "grid": '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/>',
    "share": '<path d="M12 3v12M7 8l5-5 5 5M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/>',
    "bookmark": '<path d="M6 4h12v17l-6-4-6 4z"/>',
    "inbox": '<path d="M3 13l3-8h12l3 8v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M3 13h5l1 3h6l1-3h5"/>',
    "logout": '<path d="M9 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h4M15 8l4 4-4 4M19 12H9"/>',
    "trending": '<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "moon": '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.4 1.4M17.6 17.6 19 19M5 19l1.4-1.4M17.6 6.4 19 5"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17h.01"/>',
}


def ic(name: str, size: int = 24, cls: str = "") -> str:
    body = ICONS[name]
    return (f'<svg class="ic {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def e(text) -> str:
    return html.escape(str(text), quote=True)


# --------------------------------------------------------------------------- CSS variables


def _shadow_css(layers: list, boost: float = 1.0) -> str:
    if not layers:
        return "none"
    parts = []
    for layer in layers:
        color = layer["color"]
        alpha = int(color[7:9], 16) / 255 if len(color) == 9 else 1.0
        r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        parts.append(f"{L.fmt_num(L.num(layer['offsetX']))}px {L.fmt_num(L.num(layer['offsetY']))}px "
                     f"{L.fmt_num(L.num(layer['blur']))}px {L.fmt_num(L.num(layer['spread']))}px "
                     f"rgba({r},{g},{b},{min(0.9, alpha * boost):.3f})")
    return ", ".join(parts)


def css_variables(tokens: dict) -> str:
    def stack(slot):
        fams = L.tv(tokens, f"typography.fontFamily.{slot}")
        return ", ".join(f'"{f}"' if " " in f else f for f in fams)

    root = [f"--font-display:{stack('display')}", f"--font-body:{stack('body')}", f"--font-mono:{stack('mono')}"]
    for group, prefix in (("spacing", "sp"), ("radius", "r"), ("shape", "shape"), ("borderWidth", "bw"),
                          ("iconSize", "icon"), ("size", "size")):
        for name, value in L.group_items(tokens, group):
            root.append(f"--{prefix}-{name}:{L.fmt_num(L.num(value))}px")
    for name, value in L.group_items(tokens, "motion.duration"):
        root.append(f"--dur-{name}:{L.fmt_num(L.num(value))}ms")
    for name, value in L.group_items(tokens, "motion.easing"):
        root.append(f"--ease-{name}:cubic-bezier({','.join(L.fmt_num(v) for v in value)})")
    for name, value in L.group_items(tokens, "opacity"):
        root.append(f"--op-{name}:{value}")
    out = [":root{" + ";".join(root) + "}"]
    for mode in ("light", "dark"):
        decl = [f"--c-{name}:{value}" for name, value in L.group_items(tokens, f"color.{mode}")]
        for name, value in L.group_items(tokens, "elevation"):
            decl.append(f"--el-{name[-1]}:{_shadow_css(value, 1.0 if mode == 'light' else 2.6)}")
        decl.append(f"color-scheme:{mode}")
        out.append(f'[data-theme="{mode}"]{{' + ";".join(decl) + "}")
    out.append(_effect_css(tokens))
    for role, style in L.group_items(tokens, "typography.scale"):
        raw = L.get_path(tokens, f"typography.scale.{role}")["$value"]["fontFamily"]
        var = "display" if "display" in raw else ("mono" if "mono" in raw else "body")
        out.append(f".t-{role}{{font-family:var(--font-{var});font-size:{L.fmt_num(L.num(style['fontSize']))}px;"
                   f"font-weight:{style['fontWeight']};line-height:{style['lineHeight']};"
                   f"letter-spacing:{L.fmt_num(L.num(style['letterSpacing']))}px}}")
    return "\n".join(out)


def _effect_css(tokens: dict) -> str:
    """Extra rules for non-material surface styles (tokens.effect)."""
    try:
        style = L.tv(tokens, "effect.style")
    except KeyError:
        return ""
    if style != "brutal":
        return ""
    stroke = L.fmt_num(L.num(L.tv(tokens, "effect.strokeWidth")))
    off = L.fmt_num(L.num(L.tv(tokens, "effect.shadowOffset")))
    in_dark = bool(L.tv(tokens, "effect.shadowInDark"))
    raised = ".btn--filled,.btn--danger,.iconbtn--filled,.fab,.mark,.card--elevated,.dialog"
    rules = [
        f'[data-theme="light"]{{--hard:{off}px {off}px 0 var(--c-onSurface);--stroke:var(--c-onSurface)}}',
        f'[data-theme="dark"]{{--hard:{f"{off}px {off}px 0 var(--c-onSurface)" if in_dark else "none"};'
        f'--stroke:{"var(--c-onSurface)" if in_dark else "transparent"}}}',
        f"{raised}{{border:{stroke}px solid var(--stroke)!important;box-shadow:var(--hard)!important}}",
        ".btn--filled:not(:disabled),.btn--danger:not(:disabled),.iconbtn--filled,.fab"
        "{transition:transform var(--dur-fast) var(--ease-standard),box-shadow var(--dur-fast) var(--ease-standard)}",
        f".btn--filled:not(:disabled):active,.btn--danger:not(:disabled):active,.iconbtn--filled:active,.fab:active"
        f"{{transform:translate({off}px,{off}px);box-shadow:none!important}}",
        ".btn--filled:disabled,.btn--danger:disabled{box-shadow:none!important;border-color:transparent!important}",
        f".field__box:focus-within,.field.is-focus .field__box{{border-color:var(--c-onSurface);box-shadow:none}}",
        ".chip.is-selected,.segmented button.is-selected{box-shadow:inset 0 0 0 1.5px var(--c-primary)}",
    ]
    return "\n".join(rules)


BASE_CSS = r"""
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:72px}
body{margin:0;background:var(--c-surfaceContainerLow);color:var(--c-onSurface);font-family:var(--font-body);font-size:14px;line-height:1.43;-webkit-font-smoothing:antialiased;transition:background var(--dur-normal) var(--ease-standard),color var(--dur-normal) var(--ease-standard)}
h1,h2,h3,h4,p{margin:0}
a{color:var(--c-primary)}
button,input,textarea{font:inherit;color:inherit}
.ic{flex:none;display:block}
.muted{color:var(--c-onSurfaceVariant)}
.mono{font-family:var(--font-mono)}
[data-theme="dark"] .only-light,[data-theme="light"] .only-dark{display:none!important}
.wrap{max-width:1240px;margin:0 auto;padding:0 var(--sp-xl)}
@media(max-width:600px){.wrap{padding:0 var(--sp-lg)}}

/* ---------- page chrome */
.hero{background:var(--c-surface);border-bottom:1px solid var(--c-outlineVariant);padding:var(--sp-xxxl) 0 var(--sp-xxl)}
.hero__row{display:flex;gap:var(--sp-xxl);align-items:flex-end;justify-content:space-between;flex-wrap:wrap}
.hero__id{display:flex;gap:var(--sp-lg);align-items:center;margin-bottom:var(--sp-lg)}
.mark{width:56px;height:56px;border-radius:var(--r-lg);background:var(--c-primary);color:var(--c-onPrimary);display:grid;place-items:center;font-family:var(--font-display);font-weight:700;font-size:28px;flex:none}
.hero p.lead{max-width:60ch;color:var(--c-onSurfaceVariant);margin-top:var(--sp-sm)}
.hero__meta{display:flex;flex-wrap:wrap;gap:var(--sp-sm);margin-top:var(--sp-lg)}
.tag{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:var(--r-full);border:1px solid var(--c-outlineVariant);color:var(--c-onSurfaceVariant);font-size:12px;font-weight:500;background:var(--c-surface)}
.tag b{color:var(--c-onSurface);font-weight:600}
.hero__swatch{display:flex;border-radius:var(--r-lg);overflow:hidden;box-shadow:var(--el-2);flex:none}
.hero__swatch i{width:44px;height:88px;display:block}
.topnav{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--c-surface) 88%,transparent);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--c-outlineVariant)}
.topnav__row{display:flex;align-items:center;gap:var(--sp-sm);height:56px}
.topnav__links{display:flex;gap:2px;overflow-x:auto;flex:1;scrollbar-width:none}
.topnav__links::-webkit-scrollbar{display:none}
.topnav a{padding:8px 14px;border-radius:var(--r-full);text-decoration:none;color:var(--c-onSurfaceVariant);font-weight:600;font-size:13px;white-space:nowrap;transition:background var(--dur-fast) var(--ease-standard),color var(--dur-fast) var(--ease-standard)}
.topnav a:hover{background:var(--c-surfaceContainerHigh);color:var(--c-onSurface)}
.topnav a.is-active{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.topnav__name{font-family:var(--font-display);font-weight:700;margin-right:var(--sp-sm);white-space:nowrap}
section.block{padding:var(--sp-xxxl) 0 0}
section.block:last-of-type{padding-bottom:var(--sp-huge)}
.block__head{margin-bottom:var(--sp-xl)}
.block__head .eyebrow{color:var(--c-primary);text-transform:uppercase;letter-spacing:1.2px;font-size:11px;font-weight:700;margin-bottom:4px}
.block__head p{color:var(--c-onSurfaceVariant);max-width:72ch;margin-top:6px}
.grid{display:grid;gap:var(--sp-lg);grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
.grid--wide{grid-template-columns:repeat(auto-fill,minmax(440px,1fr))}
@media(max-width:520px){.grid,.grid--wide{grid-template-columns:1fr}}
.spec{background:var(--c-surface);border:1px solid var(--c-outlineVariant);border-radius:var(--r-lg);padding:var(--sp-xl);min-width:0}
.spec--full{grid-column:1/-1}
.spec>h3{font-size:12px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--c-onSurfaceVariant);margin-bottom:var(--sp-lg);font-family:var(--font-body)}
.row{display:flex;flex-wrap:wrap;gap:var(--sp-md);align-items:center}
.col{display:flex;flex-direction:column;gap:var(--sp-md)}
.cap{font-size:11px;color:var(--c-onSurfaceVariant);font-family:var(--font-mono)}
.stack-label{display:flex;flex-direction:column;align-items:center;gap:6px}
.atomic{display:flex;flex-wrap:wrap;gap:var(--sp-sm);align-items:center;margin-top:var(--sp-lg)}
.atomic span{padding:6px 14px;border-radius:var(--r-full);background:var(--c-primaryContainer);color:var(--c-onPrimaryContainer);font-weight:600;font-size:12px}
.atomic i{color:var(--c-outline);font-style:normal}
.dodont{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-lg)}
@media(max-width:760px){.dodont{grid-template-columns:1fr}}
.dodont ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:var(--sp-md)}
.dodont li{display:flex;gap:var(--sp-md);align-items:flex-start}
.dodont .do .ic{color:var(--c-success)}.dodont .dont .ic{color:var(--c-error)}
.rationale{display:grid;gap:var(--sp-lg);grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.rationale h4{font-family:var(--font-display);font-size:16px;margin-bottom:6px}

/* ---------- tokens */
.ramp{display:grid;grid-template-columns:repeat(auto-fit,minmax(54px,1fr));border-radius:var(--r-md);overflow:hidden;border:1px solid var(--c-outlineVariant)}
.ramp div{height:64px;padding:6px;display:flex;flex-direction:column;justify-content:space-between;font-family:var(--font-mono);font-size:10px;cursor:pointer;border:0}
.ramp div b{font-size:11px}
.ramp-title{display:flex;justify-content:space-between;margin:var(--sp-lg) 0 6px;font-weight:600}
.ramp-title:first-of-type{margin-top:0}
.roles{display:grid;gap:var(--sp-sm);grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
.role{border-radius:var(--r-md);padding:12px;min-height:84px;display:flex;flex-direction:column;justify-content:space-between;border:1px solid var(--c-outlineVariant);font-size:12px}
.role b{font-weight:600;word-break:break-word}
.role small{font-family:var(--font-mono);font-size:10.5px;display:flex;justify-content:space-between;gap:6px;opacity:.95}
table.pairs{width:100%;border-collapse:collapse;font-size:12.5px}
table.pairs th{text-align:left;font-weight:600;color:var(--c-onSurfaceVariant);padding:6px 8px;border-bottom:1px solid var(--c-outlineVariant);position:sticky;top:0;background:var(--c-surface)}
table.pairs td{padding:6px 8px;border-bottom:1px solid var(--c-outlineVariant)}
.pairs-scroll{max-height:380px;overflow:auto}
.chipdemo{display:inline-block;padding:2px 10px;border-radius:var(--r-sm);font-weight:600;border:1px solid var(--c-outlineVariant)}
.ok{color:var(--c-success);font-weight:700}.bad{color:var(--c-error);font-weight:700}
.type-row{display:grid;grid-template-columns:150px 1fr;gap:var(--sp-lg);align-items:baseline;padding:10px 0;border-bottom:1px solid var(--c-outlineVariant)}
.type-row:last-child{border:0}
.type-row>div:last-child{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media(max-width:600px){.type-row{grid-template-columns:1fr;gap:2px}}
.space-row{display:flex;align-items:center;gap:var(--sp-md);padding:4px 0}
.space-row i{height:16px;background:var(--c-primary);border-radius:2px;display:block;min-width:1px}
.space-row .cap{width:104px;flex:none}
.box{width:72px;height:72px;background:var(--c-primaryContainer);border:1px solid var(--c-primary);display:block}
.elev{width:88px;height:72px;background:var(--c-surfaceContainerLowest);border-radius:var(--r-md);display:grid;place-items:center;font-family:var(--font-mono);font-size:11px}
.motion-track{height:28px;border-radius:var(--r-full);background:var(--c-surfaceContainerHigh);position:relative;overflow:hidden;flex:1;min-width:120px}
.motion-track i{position:absolute;top:4px;left:4px;width:20px;height:20px;border-radius:50%;background:var(--c-primary)}
.motion-row{display:flex;gap:var(--sp-md);align-items:center;padding:5px 0}
.motion-row .cap{width:150px;flex:none}
.motion-row:hover i,.spec.is-play .motion-track i{left:calc(100% - 24px)}

/* ---------- atoms */
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:var(--sp-sm);height:var(--size-buttonMd);min-width:64px;padding:0 var(--sp-xl);border-radius:var(--shape-button);border:var(--bw-thin) solid transparent;background:transparent;cursor:pointer;white-space:nowrap;text-decoration:none;font-family:var(--font-body);transition:box-shadow var(--dur-fast) var(--ease-standard),transform var(--dur-fast) var(--ease-standard);overflow:hidden}
.btn::after{content:"";position:absolute;inset:0;background:currentColor;opacity:0;transition:opacity var(--dur-fast) var(--ease-standard);pointer-events:none}
.btn:hover::after,.btn.is-hover::after{opacity:var(--op-hover)}
.btn:active::after,.btn.is-pressed::after{opacity:.16}
.btn:active{transform:scale(.98)}
.btn:focus-visible,.btn.is-focus{outline:var(--bw-focus) solid var(--c-primary);outline-offset:2px}
.btn--sm{height:var(--size-buttonSm);padding:0 var(--sp-lg)}
.btn--lg{height:var(--size-buttonLg);padding:0 var(--sp-xxl)}
.btn--block{display:flex;width:100%}
.btn--filled{background:var(--c-primary);color:var(--c-onPrimary)}
.btn--tonal{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.btn--outlined{border-color:var(--c-outline);color:var(--c-primary)}
.btn--text{color:var(--c-primary);padding:0 var(--sp-md)}
.btn--elevated{background:var(--c-surfaceContainerLow);color:var(--c-primary);box-shadow:var(--el-1)}
.btn--danger{background:var(--c-error);color:var(--c-onError)}
.btn--danger-text{color:var(--c-error);padding:0 var(--sp-md)}
.btn:disabled,.btn.is-disabled{background:color-mix(in srgb,var(--c-onSurface) 12%,transparent);color:color-mix(in srgb,var(--c-onSurface) 38%,transparent);border-color:transparent;cursor:not-allowed;box-shadow:none}
.btn--outlined:disabled,.btn--text:disabled{background:transparent}
.btn--outlined:disabled{border-color:color-mix(in srgb,var(--c-onSurface) 12%,transparent)}
.btn:disabled::after{display:none}
.iconbtn{width:var(--size-touchTarget);height:var(--size-touchTarget);border-radius:var(--r-full);border:0;background:transparent;color:var(--c-onSurfaceVariant);display:inline-grid;place-items:center;cursor:pointer;position:relative;flex:none}
.iconbtn:hover{background:color-mix(in srgb,var(--c-onSurface) 8%,transparent)}
.iconbtn--filled{background:var(--c-primary);color:var(--c-onPrimary)}
.iconbtn--tonal{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.iconbtn--scrim{background:color-mix(in srgb,var(--c-surface) 86%,transparent);color:var(--c-onSurface)}
.fab{width:56px;height:56px;border-radius:var(--r-lg);border:0;background:var(--c-primaryContainer);color:var(--c-onPrimaryContainer);box-shadow:var(--el-3);display:grid;place-items:center;cursor:pointer}
.spinner{width:18px;height:18px;border-radius:50%;border:2px solid currentColor;border-right-color:transparent;animation:spin .8s linear infinite}
.spinner--lg{width:36px;height:36px;border-width:4px;color:var(--c-primary)}
@keyframes spin{to{transform:rotate(360deg)}}

.field{display:flex;flex-direction:column;gap:6px;min-width:0}
.field__label{color:var(--c-onSurface)}
.field__box{display:flex;align-items:center;gap:var(--sp-sm);min-height:var(--size-input);padding:0 var(--sp-lg);border-radius:var(--shape-input);border:var(--bw-thin) solid var(--c-outline);background:var(--c-surfaceContainerLowest);color:var(--c-onSurfaceVariant);transition:border-color var(--dur-fast) var(--ease-standard),box-shadow var(--dur-fast) var(--ease-standard)}
.field__box input,.field__box textarea{flex:1;min-width:0;border:0;outline:0;background:transparent;color:var(--c-onSurface);font-size:16px;padding:0;height:100%}
.field__box textarea{resize:none;padding:var(--sp-md) 0;height:88px;line-height:1.5}
.field__box input::placeholder,.field__box textarea::placeholder{color:var(--c-onSurfaceVariant);opacity:1}
.field__box:focus-within,.field.is-focus .field__box{border-color:var(--c-primary);box-shadow:0 0 0 1px var(--c-primary)}
.field__help{color:var(--c-onSurfaceVariant);display:flex;gap:6px;align-items:center}
.field.is-error .field__box{border-color:var(--c-error);box-shadow:0 0 0 1px var(--c-error)}
.field.is-error .field__help,.field.is-error .field__label{color:var(--c-error)}
.field.is-disabled{opacity:var(--op-disabled);pointer-events:none}
.field.is-disabled .field__box{background:transparent}

.check{display:inline-flex;align-items:center;gap:var(--sp-sm);min-height:var(--size-touchTarget);cursor:pointer}
.check input{appearance:none;-webkit-appearance:none;margin:0;width:20px;height:20px;border:2px solid var(--c-onSurfaceVariant);border-radius:var(--r-xs);display:grid;place-items:center;cursor:pointer;flex:none;transition:background var(--dur-fast) var(--ease-standard),border-color var(--dur-fast) var(--ease-standard)}
.check input[type=radio]{border-radius:50%}
.check input:checked{background:var(--c-primary);border-color:var(--c-primary)}
.check input[type=checkbox]:checked::after{content:"";width:10px;height:5px;border-left:2px solid var(--c-onPrimary);border-bottom:2px solid var(--c-onPrimary);transform:rotate(-45deg) translate(1px,-1px)}
.check input[type=radio]:checked{background:transparent}
.check input[type=radio]:checked::after{content:"";width:10px;height:10px;border-radius:50%;background:var(--c-primary)}
.check input:focus-visible,.switch input:focus-visible{outline:var(--bw-focus) solid var(--c-primary);outline-offset:2px}
.check input:disabled{opacity:var(--op-disabled);cursor:not-allowed}
.switch{display:inline-flex;align-items:center;min-height:var(--size-touchTarget);cursor:pointer}
.switch input{appearance:none;-webkit-appearance:none;margin:0;width:52px;height:32px;border-radius:var(--r-full);background:var(--c-surfaceContainerHighest);border:2px solid var(--c-outline);position:relative;cursor:pointer;transition:background var(--dur-normal) var(--ease-standard),border-color var(--dur-normal) var(--ease-standard);flex:none}
.switch input::after{content:"";position:absolute;top:50%;left:6px;width:16px;height:16px;border-radius:50%;background:var(--c-outline);transform:translateY(-50%);transition:all var(--dur-normal) var(--ease-emphasized)}
.switch input:checked{background:var(--c-primary);border-color:var(--c-primary)}
.switch input:checked::after{left:22px;width:24px;height:24px;background:var(--c-onPrimary)}
.switch input:disabled{opacity:var(--op-disabled);cursor:not-allowed}
.chip{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 var(--sp-md);border-radius:var(--shape-chip);border:var(--bw-thin) solid var(--c-outline);background:transparent;color:var(--c-onSurfaceVariant);cursor:pointer;white-space:nowrap;font-family:var(--font-body)}
.chip.is-selected{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer);border-color:transparent}
.chip--tertiary{background:var(--c-tertiaryContainer);color:var(--c-onTertiaryContainer);border-color:transparent}
.badge{display:inline-flex;align-items:center;justify-content:center;min-width:20px;height:20px;padding:0 6px;border-radius:var(--r-full);background:var(--c-error);color:var(--c-onError);font-size:11px;font-weight:700;line-height:1}
.badge--dot{min-width:10px;width:10px;height:10px;padding:0;border:2px solid var(--c-surface);box-sizing:content-box}
.status{display:inline-flex;align-items:center;gap:4px;height:24px;padding:0 10px 0 6px;border-radius:var(--r-full);font-size:12px;font-weight:600;white-space:nowrap}
.status--success{background:var(--c-successContainer);color:var(--c-onSuccessContainer)}
.status--warning{background:var(--c-warningContainer);color:var(--c-onWarningContainer)}
.status--error{background:var(--c-errorContainer);color:var(--c-onErrorContainer)}
.status--info{background:var(--c-infoContainer);color:var(--c-onInfoContainer)}
.status--neutral{background:var(--c-surfaceContainerHighest);color:var(--c-onSurfaceVariant);padding:0 10px}
.avatar{width:var(--size-avatarMd);height:var(--size-avatarMd);border-radius:50%;background:var(--c-primaryContainer);color:var(--c-onPrimaryContainer);display:inline-grid;place-items:center;font-weight:700;font-size:14px;flex:none;position:relative}
.avatar--sm{width:var(--size-avatarSm);height:var(--size-avatarSm);font-size:12px}
.avatar--lg{width:var(--size-avatarLg);height:var(--size-avatarLg);font-size:22px}
.avatar--b{background:var(--c-tertiaryContainer);color:var(--c-onTertiaryContainer)}
.avatar--c{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.divider{height:1px;background:var(--c-outlineVariant);border:0;margin:0;width:100%}
.progress{height:6px;border-radius:var(--r-full);background:var(--c-surfaceContainerHighest);overflow:hidden;position:relative;width:100%}
.progress i{position:absolute;inset:0 auto 0 0;background:var(--c-primary);border-radius:inherit}
.progress--ind i{width:40%;animation:ind 1.6s var(--ease-standard) infinite}
@keyframes ind{0%{left:-40%}100%{left:100%}}
.thumb{background:linear-gradient(135deg,var(--c-primaryContainer),var(--c-tertiaryContainer));color:var(--c-onPrimaryContainer);display:grid;place-items:center;border-radius:var(--r-md);flex:none}
.thumb--b{background:linear-gradient(135deg,var(--c-secondaryContainer),var(--c-primaryContainer))}
.thumb--c{background:linear-gradient(135deg,var(--c-tertiaryContainer),var(--c-secondaryContainer))}
.icons{display:grid;grid-template-columns:repeat(auto-fill,minmax(56px,1fr));gap:var(--sp-sm)}
.icons div{display:grid;place-items:center;height:56px;border-radius:var(--r-md);background:var(--c-surfaceContainer);color:var(--c-onSurfaceVariant)}

/* ---------- molecules */
.searchbar{display:flex;align-items:center;gap:var(--sp-md);height:var(--size-input);padding:0 var(--sp-lg);border-radius:var(--r-full);background:var(--c-surfaceContainerHigh);color:var(--c-onSurfaceVariant)}
.searchbar input{flex:1;min-width:0;border:0;outline:0;background:transparent;color:var(--c-onSurface);font-size:16px}
.searchbar input::placeholder{color:var(--c-onSurfaceVariant);opacity:1}
.tile{display:flex;align-items:center;gap:var(--sp-lg);min-height:var(--size-listItem);padding:var(--sp-sm) var(--sp-lg);color:var(--c-onSurface);text-decoration:none}
.tile__body{flex:1;min-width:0}
.tile__body>*{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tile__sub{color:var(--c-onSurfaceVariant)}
.tile__lead{color:var(--c-onSurfaceVariant);display:grid;place-items:center;width:40px;height:40px;border-radius:var(--r-md);background:var(--c-surfaceContainerHigh);flex:none}
.tile__trail{color:var(--c-onSurfaceVariant);display:flex;align-items:center;gap:var(--sp-sm);flex:none}
.cardhead{display:flex;align-items:center;gap:var(--sp-md);padding:var(--sp-lg)}
.cardhead__body{flex:1;min-width:0}
.snackbar{display:flex;align-items:center;gap:var(--sp-md);min-height:48px;padding:6px 6px 6px var(--sp-lg);border-radius:var(--r-sm);background:var(--c-inverseSurface);color:var(--c-onInverseSurface);box-shadow:var(--el-3)}
.snackbar span{flex:1}
.snackbar button{border:0;background:transparent;color:var(--c-inversePrimary);font-weight:700;height:36px;padding:0 var(--sp-md);border-radius:var(--r-sm);cursor:pointer}
.segmented{display:flex;border:var(--bw-thin) solid var(--c-outline);border-radius:var(--r-full);overflow:hidden;height:40px}
.segmented button{flex:1;border:0;border-right:var(--bw-thin) solid var(--c-outline);background:transparent;color:var(--c-onSurface);cursor:pointer;display:flex;gap:6px;align-items:center;justify-content:center;padding:0 var(--sp-md);font-family:var(--font-body);transition:background var(--dur-fast) var(--ease-standard)}
.segmented button:last-child{border-right:0}
.segmented button.is-selected{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.segmented button .ic{display:none}
.segmented button.is-selected .ic{display:block}
.banner{display:flex;gap:var(--sp-md);align-items:flex-start;padding:var(--sp-md) var(--sp-lg);border-radius:var(--r-md)}
.banner--info{background:var(--c-infoContainer);color:var(--c-onInfoContainer)}
.banner--warning{background:var(--c-warningContainer);color:var(--c-onWarningContainer)}

/* ---------- organisms */
.appbar{display:flex;align-items:center;gap:var(--sp-xs);height:var(--size-appBar);padding:0 var(--sp-xs);background:var(--c-surface);color:var(--c-onSurface);flex:none}
.appbar__title{flex:1;min-width:0;padding:0 var(--sp-md);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.appbar--pad{padding:0 var(--sp-lg)}
.navbar{display:flex;height:var(--size-navBar);background:var(--c-surfaceContainer);flex:none}
.navbar a{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:var(--c-onSurfaceVariant);text-decoration:none;font-size:12px;font-weight:500}
.navbar a span.pill{width:64px;height:32px;border-radius:var(--r-full);display:grid;place-items:center;transition:background var(--dur-normal) var(--ease-standard)}
.navbar a.is-active{color:var(--c-onSurface);font-weight:700}
.navbar a.is-active span.pill{background:var(--c-secondaryContainer);color:var(--c-onSecondaryContainer)}
.card{background:var(--c-surfaceContainerLow);border-radius:var(--shape-card);overflow:hidden;border:1px solid var(--c-outlineVariant)}
.card--elevated{border:0;box-shadow:var(--el-1);background:var(--c-surfaceContainerLowest)}
.card--filled{border:0;background:var(--c-primaryContainer);color:var(--c-onPrimaryContainer)}
.card__body{padding:var(--sp-lg);display:flex;flex-direction:column;gap:var(--sp-sm)}
.card__actions{display:flex;justify-content:flex-end;gap:var(--sp-sm);padding:0 var(--sp-lg) var(--sp-lg)}
.listsec__head{display:flex;justify-content:space-between;align-items:center;padding:var(--sp-lg) var(--sp-lg) var(--sp-xs);color:var(--c-onSurfaceVariant)}
.dialog{background:var(--c-surfaceContainerHigh);border-radius:var(--shape-dialog);padding:var(--sp-xl);box-shadow:var(--el-3);max-width:320px;display:flex;flex-direction:column;gap:var(--sp-lg)}
.dialog__actions{display:flex;justify-content:flex-end;gap:var(--sp-sm)}
.scrimbox{background:color-mix(in srgb,var(--c-scrim) 32%,var(--c-surface));border-radius:var(--r-md);padding:var(--sp-xl);display:grid;place-items:center}
.empty{display:flex;flex-direction:column;align-items:center;text-align:center;gap:var(--sp-md);padding:var(--sp-xxl) var(--sp-xl)}
.empty__art{width:96px;height:96px;border-radius:50%;background:var(--c-surfaceContainerHigh);color:var(--c-onSurfaceVariant);display:grid;place-items:center}
.sheet{background:var(--c-surfaceContainerLow);border-radius:var(--shape-sheet) var(--shape-sheet) 0 0;padding:var(--sp-sm) var(--sp-lg) var(--sp-lg);box-shadow:var(--el-2)}
.sheet__grab{width:32px;height:4px;border-radius:2px;background:var(--c-outline);margin:6px auto var(--sp-lg)}

/* ---------- phones */
.phones{display:flex;gap:var(--sp-xxl);overflow-x:auto;padding:var(--sp-sm) var(--sp-xl) var(--sp-xl);scroll-snap-type:x proximity;margin:0 calc(var(--sp-xl) * -1)}
.phonewrap{flex:none;scroll-snap-align:center;display:flex;flex-direction:column;gap:var(--sp-md);align-items:center}
.phonewrap figcaption{font-weight:700;font-family:var(--font-display);font-size:16px}
.phonewrap figcaption small{display:block;font-weight:400;font-family:var(--font-body);color:var(--c-onSurfaceVariant);font-size:12px;text-align:center}
figure{margin:0}
.phone{width:360px;height:740px;border-radius:44px;border:10px solid var(--c-inverseSurface);background:var(--c-background);color:var(--c-onSurface);overflow:hidden;display:flex;flex-direction:column;box-shadow:var(--el-4);position:relative}
.statusbar{height:32px;display:flex;justify-content:space-between;align-items:center;padding:0 var(--sp-xl);font-size:12px;font-weight:600;flex:none;background:inherit}
.statusbar i{display:inline-block;width:16px;height:9px;border-radius:2px;border:1.5px solid currentColor;position:relative}
.statusbar i::after{content:"";position:absolute;inset:1px 4px 1px 1px;background:currentColor;border-radius:1px}
.screen{flex:1;overflow-y:auto;overflow-x:hidden;scrollbar-width:none;display:flex;flex-direction:column}
.screen::-webkit-scrollbar{display:none}
.pad{padding:var(--sp-lg)}
.padx{padding-left:var(--sp-lg);padding-right:var(--sp-lg)}
.gap-xs{gap:var(--sp-xs)}.gap-sm{gap:var(--sp-sm)}.gap-md{gap:var(--sp-md)}.gap-lg{gap:var(--sp-lg)}.gap-xl{gap:var(--sp-xl)}
.grow{flex:1}.center{text-align:center}.between{justify-content:space-between}
.hscroll{display:flex;gap:var(--sp-sm);overflow-x:auto;padding:0 var(--sp-lg);scrollbar-width:none;flex:none}
.hscroll::-webkit-scrollbar{display:none}
.bottombar{display:flex;gap:var(--sp-md);padding:var(--sp-md) var(--sp-lg);background:var(--c-surface);border-top:1px solid var(--c-outlineVariant);flex:none}
.orline{display:flex;align-items:center;gap:var(--sp-md);color:var(--c-onSurfaceVariant)}
.orline::before,.orline::after{content:"";flex:1;height:1px;background:var(--c-outlineVariant)}
.kv{display:flex;justify-content:space-between;gap:var(--sp-lg);padding:var(--sp-md) 0;border-bottom:1px solid var(--c-outlineVariant)}
.kv:last-child{border:0}
.statgrid{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-md)}
.stat{background:var(--c-surfaceContainerLow);border:1px solid var(--c-outlineVariant);border-radius:var(--shape-card);padding:var(--sp-lg);display:flex;flex-direction:column;gap:var(--sp-xs)}
.fabpos{position:absolute;right:16px;bottom:calc(var(--size-navBar) + 16px)}

/* ---------- templates (wireframes) */
.wf{width:216px;height:432px;border-radius:24px;border:6px solid var(--c-outline);background:var(--c-surface);padding:8px;display:flex;flex-direction:column;gap:6px;overflow:hidden}
.wf div{border:1.5px dashed var(--c-outline);border-radius:var(--r-sm);display:grid;place-items:center;color:var(--c-onSurfaceVariant);font-size:10.5px;font-weight:600;text-align:center;padding:2px 6px;min-height:22px;background:var(--c-surfaceContainerLow)}
.wf div.p{background:var(--c-primaryContainer);color:var(--c-onPrimaryContainer);border-color:var(--c-primary)}
.wf div.g{flex:1}
.wf .wfrow{display:flex;gap:6px;border:0;padding:0;background:transparent;min-height:0}
.wf .wfrow>div{flex:1}
.tpl{display:flex;flex-direction:column;gap:var(--sp-md);align-items:center;flex:none;width:232px}
.tpl p{font-size:12px;color:var(--c-onSurfaceVariant);text-align:center}
.tpls{display:flex;gap:var(--sp-xl);overflow-x:auto;padding-bottom:var(--sp-md)}
footer.foot{border-top:1px solid var(--c-outlineVariant);padding:var(--sp-xl) 0;color:var(--c-onSurfaceVariant);font-size:12px;background:var(--c-surface)}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}
"""

SCRIPT = r"""
(function(){
  var root=document.documentElement,key='designku-theme';
  function set(t){root.setAttribute('data-theme',t);try{localStorage.setItem(key,t)}catch(e){}
    var b=document.getElementById('themeBtn');if(b){b.setAttribute('aria-pressed',t==='dark');b.querySelector('.lbl').textContent=t==='dark'?'Dark':'Light'}}
  var saved=null;try{saved=localStorage.getItem(key)}catch(e){}
  if(location.hash==='#dark'||location.hash==='#light'){saved=location.hash.slice(1)}
  set(saved||(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
  document.addEventListener('click',function(ev){
    var t=ev.target.closest('#themeBtn');if(t){set(root.getAttribute('data-theme')==='dark'?'light':'dark');return}
    var s=ev.target.closest('.segmented button');if(s){s.parentNode.querySelectorAll('button').forEach(function(b){b.classList.toggle('is-selected',b===s);b.setAttribute('aria-pressed',b===s)});return}
    var c=ev.target.closest('.chip[data-toggle]');if(c){c.classList.toggle('is-selected');return}
    var h=ev.target.closest('[data-hex]');if(h&&navigator.clipboard){navigator.clipboard.writeText(h.getAttribute('data-hex')).catch(function(){})}
    var m=ev.target.closest('#motionPlay');if(m){var sp=m.closest('.spec');sp.classList.toggle('is-play')}
  });
  document.addEventListener('keydown',function(ev){if((ev.key==='d'||ev.key==='D')&&!/input|textarea/i.test(ev.target.tagName)&&!ev.metaKey&&!ev.ctrlKey){set(root.getAttribute('data-theme')==='dark'?'light':'dark')}});
  var links=[].slice.call(document.querySelectorAll('.topnav__links a'));
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){links.forEach(function(a){a.classList.toggle('is-active',a.getAttribute('href')==='#'+en.target.id)})}})},{rootMargin:'-20% 0px -70% 0px'});
    document.querySelectorAll('section.block').forEach(function(s){io.observe(s)});
  }
})();
"""

# --------------------------------------------------------------------------- small builders


def btn(label, kind="filled", size="", extra="", icon="", attrs=""):
    cls = f"btn btn--{kind} t-labelLarge" + (f" btn--{size}" if size else "") + (f" {extra}" if extra else "")
    return f'<button type="button" class="{cls}" {attrs}>{ic(icon, 18) if icon else ""}{e(label)}</button>'


def field(label, placeholder="", value="", state="", helper="", lead="", trail="", kind="text", area=False):
    cls = "field" + (f" is-{state}" if state else "")
    control = (f'<textarea placeholder="{e(placeholder)}">{e(value)}</textarea>' if area else
               f'<input type="{kind}" placeholder="{e(placeholder)}" value="{e(value)}"'
               f'{" disabled" if state == "disabled" else ""}{" aria-invalid=true" if state == "error" else ""}>')
    help_icon = ic("alert", 16) if state == "error" else ""
    help_html = f'<span class="field__help t-bodySmall">{help_icon}{e(helper)}</span>' if helper else ""
    return (f'<label class="{cls}"><span class="field__label t-labelLarge">{e(label)}</span>'
            f'<span class="field__box">{ic(lead, 20) if lead else ""}{control}{ic(trail, 20) if trail else ""}</span>{help_html}</label>')


def status(kind, label):
    icon = {"success": "check-circle", "warning": "alert", "error": "x-circle", "info": "info"}.get(kind)
    return f'<span class="status status--{kind}">{ic(icon, 14) if icon else ""}{e(label)}</span>'


def tile(title, sub="", lead="", trail="", lead_html=""):
    lead_part = lead_html or (f'<span class="tile__lead">{ic(lead, 20)}</span>' if lead else "")
    sub_part = f'<div class="tile__sub t-bodyMedium">{e(sub)}</div>' if sub else ""
    return (f'<div class="tile">{lead_part}<div class="tile__body"><div class="t-titleMedium">{e(title)}</div>{sub_part}</div>'
            f'<div class="tile__trail">{trail}</div></div>')


def navbar(active=0):
    items = [("home", "Home"), ("list", "Browse"), ("bookmark", "Saved"), ("user", "Profile")]
    return '<nav class="navbar" aria-label="Bottom navigation">' + "".join(
        f'<a href="#pages" class="{"is-active" if i == active else ""}"><span class="pill">{ic(icon, 22)}</span>{label}</a>'
        for i, (icon, label) in enumerate(items)) + "</nav>"


def appbar(title, lead="arrow-left", actions=(), style="t-titleLarge"):
    lead_html = f'<button class="iconbtn" aria-label="Back">{ic(lead)}</button>' if lead else ""
    acts = "".join(f'<button class="iconbtn" aria-label="{a}">{ic(a)}</button>' for a in actions)
    return (f'<header class="appbar{"" if lead else " appbar--pad"}">{lead_html}'
            f'<div class="appbar__title {style}"{"" if lead else " style=padding-left:0"}>{e(title)}</div>{acts}</header>')


def phone(title, note, body, extra=""):
    return (f'<figure class="phonewrap"><div class="phone"><div class="statusbar"><span>9:41</span><i></i></div>'
            f'{body}{extra}</div><figcaption>{e(title)}<small>{e(note)}</small></figcaption></figure>')


def spec(title, body, cls=""):
    return f'<div class="spec {cls}"><h3>{e(title)}</h3>{body}</div>'


def section(anchor, eyebrow, title, desc, body):
    return (f'<section class="block" id="{anchor}"><div class="wrap"><div class="block__head"><div class="eyebrow">{e(eyebrow)}</div>'
            f'<h2 class="t-headlineMedium">{e(title)}</h2><p class="t-bodyLarge">{desc}</p></div>{body}</div></section>')


# --------------------------------------------------------------------------- sections


def _tokens_section(tokens: dict) -> str:
    info = L.meta(tokens)
    level = (info.get("spec") or {}).get("contrast", "AA")
    out = []

    # palette ramps
    ramps = []
    for name, group in tokens["color"]["palette"].items():
        cells = []
        for tone, token in group.items():
            hex_value = token["$value"]
            fg = "#FFFFFF" if L.contrast("#FFFFFF", hex_value) >= L.contrast("#000000", hex_value) else "#000000"
            cells.append(f'<div style="background:{hex_value};color:{fg}" data-hex="{hex_value}" title="{name}.{tone} {hex_value} — click to copy">'
                         f'<b>{tone}</b><span>{hex_value[1:]}</span></div>')
        ramps.append(f'<div class="ramp-title"><span>{e(name)}</span><span class="cap">color.palette.{e(name)}.*</span></div>'
                     f'<div class="ramp">{"".join(cells)}</div>')
    out.append(spec("Primitive palette — tonal scales (tone = CIE L*)", "".join(ramps), "spec--full"))

    # semantic roles
    def role_tile(role, on_role):
        ratios = {m: L.contrast(L.tv(tokens, f"color.{m}.{role}"), L.tv(tokens, f"color.{m}.{on_role}")) for m in ("light", "dark")}
        hexes = {m: L.tv(tokens, f"color.{m}.{role}") for m in ("light", "dark")}
        small = "".join(f'<small class="only-{m}"><span>{hexes[m]}</span><span>{ratios[m]:.1f}:1</span></small>' for m in ("light", "dark"))
        return f'<div class="role" style="background:var(--c-{role});color:var(--c-{on_role})"><b>{role}</b>{small}</div>'

    groups = [
        ("Brand", [(f, "on" + f.capitalize()) for f in ("primary", "secondary", "tertiary")]
         + [(f + "Container", "on" + f.capitalize() + "Container") for f in ("primary", "secondary", "tertiary")]),
        ("Status", [(f, "on" + f.capitalize()) for f in ("error", "success", "warning", "info")]
         + [(f + "Container", "on" + f.capitalize() + "Container") for f in ("error", "success", "warning", "info")]),
        ("Surfaces", [("background", "onBackground")] + [(s, "onSurface") for s in ds_validate.SURFACES]
         + [("surfaceVariant", "onSurfaceVariant"), ("inverseSurface", "onInverseSurface"),
            ("outline", "surface"), ("outlineVariant", "onSurface")]),
    ]
    roles_html = "".join(
        f'<div class="ramp-title"><span>{title}</span><span class="cap">text shown in its paired on-color, with measured contrast</span></div>'
        f'<div class="roles">{"".join(role_tile(r, o) for r, o in items)}</div>' for title, items in groups)
    out.append(spec("Semantic colors — the only colors UI code may use", roles_html, "spec--full"))

    # contrast table
    tables = []
    for mode in ("light", "dark"):
        rows = ds_validate.measure(tokens, mode, level)
        body = "".join(
            f'<tr><td><span class="chipdemo" style="color:{r["fgHex"]};background:{r["bgHex"]}">Aa</span></td>'
            f'<td class="mono">{r["fg"]}</td><td class="mono">{r["bg"]}</td><td>{e(r["usage"])}</td>'
            f'<td class="mono">{r["ratio"]:.2f}:1</td><td class="mono">≥ {r["min"]:g}</td>'
            f'<td class="{"ok" if r["pass"] else "bad"}">{"Pass" if r["pass"] else "Fail"}</td></tr>' for r in rows)
        passed = sum(1 for r in rows if r["pass"])
        tables.append(f'<div class="only-{mode}"><p class="muted" style="margin-bottom:12px">{passed}/{len(rows)} pairs pass WCAG 2.2 {level} in {mode} mode '
                      f'(text ≥ {"7" if level == "AAA" else "4.5"}:1, UI components ≥ 3:1).</p><div class="pairs-scroll"><table class="pairs">'
                      f'<thead><tr><th></th><th>Foreground</th><th>Background</th><th>Usage</th><th>Ratio</th><th>Min</th><th></th></tr></thead>'
                      f'<tbody>{body}</tbody></table></div></div>')
    out.append(spec("Contrast audit", "".join(tables), "spec--full"))

    # typography
    type_rows = []
    for role, style in L.group_items(tokens, "typography.scale"):
        size = L.fmt_num(L.num(style["fontSize"]))
        sample = "The quick brown fox 0123456789" if not role.startswith("display") else "Aa Bb 123"
        type_rows.append(f'<div class="type-row"><div class="cap">{role}<br>{size}px / {style["fontWeight"]} / {style["lineHeight"]}</div>'
                         f'<div class="t-{role}">{sample}</div></div>')
    fonts = info.get("fonts", {})
    out.append(spec(f"Typography — {fonts.get('display')} (display) · {fonts.get('body')} (body) · {fonts.get('mono')} (mono)",
                    "".join(type_rows), "spec--full"))

    # spacing
    out.append(spec("Spacing — 4pt grid", "".join(
        f'<div class="space-row"><span class="cap">spacing.{n} · {L.fmt_num(L.num(v))}</span><i style="width:{L.fmt_num(L.num(v))}px"></i></div>'
        for n, v in L.group_items(tokens, "spacing"))))
    # radius + shape
    radius_html = '<div class="row">' + "".join(
        f'<div class="stack-label"><span class="box" style="border-radius:{min(L.num(v), 36):g}px"></span><span class="cap">{n} · {L.fmt_num(L.num(v))}</span></div>'
        for n, v in L.group_items(tokens, "radius")) + "</div>"
    shape_html = '<p class="cap" style="margin-top:16px">' + " · ".join(
        f'shape.{n} → {L.alias_of(tokens, "shape." + n) or L.fmt_num(L.num(v))}' for n, v in L.group_items(tokens, "shape")) + "</p>"
    out.append(spec("Radius and component shape", radius_html + shape_html))
    # elevation
    out.append(spec("Elevation", '<div class="row" style="gap:24px;padding:8px">' + "".join(
        f'<div class="elev" style="box-shadow:var(--el-{n[-1]})">{n}</div>' for n, _ in L.group_items(tokens, "elevation")) + "</div>"))
    # borders + icons + sizes
    misc = '<div class="row" style="gap:24px;align-items:flex-end">' + "".join(
        f'<div class="stack-label"><span style="display:block;width:64px;height:40px;border-radius:var(--r-sm);border:{L.fmt_num(L.num(v))}px solid var(--c-outline)"></span>'
        f'<span class="cap">borderWidth.{n} · {L.fmt_num(L.num(v))}</span></div>' for n, v in L.group_items(tokens, "borderWidth")) + "</div>"
    misc += '<div class="row" style="gap:24px;align-items:flex-end;margin-top:24px">' + "".join(
        f'<div class="stack-label">{ic("star", int(L.num(v)))}<span class="cap">iconSize.{n} · {L.fmt_num(L.num(v))}</span></div>'
        for n, v in L.group_items(tokens, "iconSize")) + "</div>"
    misc += '<p class="cap" style="margin-top:20px;line-height:1.8">' + " · ".join(
        f"size.{n} {L.fmt_num(L.num(v))}" for n, v in L.group_items(tokens, "size")) + "</p>"
    out.append(spec("Borders, icon sizes, component sizes", misc))
    # motion
    motion = "".join(
        f'<div class="motion-row"><span class="cap">duration.{n} · {L.fmt_num(L.num(v))}ms</span>'
        f'<span class="motion-track"><i style="transition:left {L.fmt_num(L.num(v))}ms var(--ease-standard)"></i></span></div>'
        for n, v in L.group_items(tokens, "motion.duration") if L.num(v) > 0)
    motion += "".join(
        f'<div class="motion-row"><span class="cap">easing.{n}</span>'
        f'<span class="motion-track"><i style="transition:left var(--dur-slower) var(--ease-{n})"></i></span></div>'
        for n, _ in L.group_items(tokens, "motion.easing"))
    motion += f'<div style="margin-top:12px">{btn("Play all", "tonal", "sm", attrs="id=motionPlay")}<span class="cap" style="margin-left:12px">or hover a row</span></div>'
    out.append(spec("Motion — durations and easing", motion))
    return '<div class="grid grid--wide">' + "".join(out) + "</div>"


def _atoms_section() -> str:
    out = []
    kinds = [("filled", "Filled"), ("tonal", "Tonal"), ("outlined", "Outlined"), ("text", "Text"), ("elevated", "Elevated"), ("danger", "Delete")]
    out.append(spec("Button — variants", '<div class="row">' + "".join(btn(lbl, k) for k, lbl in kinds) + "</div>"
                    + '<div class="row" style="margin-top:16px">' + btn("Small", "filled", "sm") + btn("Medium", "filled") + btn("Large", "filled", "lg")
                    + btn("With icon", "tonal", icon="plus") + "</div>"))
    states = (btn("Default", "filled") + btn("Hover", "filled", extra="is-hover") + btn("Pressed", "filled", extra="is-pressed")
              + btn("Focus", "filled", extra="is-focus") + btn("Disabled", "filled", attrs="disabled")
              + f'<button type="button" class="btn btn--filled t-labelLarge" aria-busy="true"><span class="spinner"></span>Loading</button>')
    states2 = (btn("Default", "outlined") + btn("Hover", "outlined", extra="is-hover") + btn("Focus", "outlined", extra="is-focus")
               + btn("Disabled", "outlined", attrs="disabled") + btn("Disabled", "text", attrs="disabled"))
    out.append(spec("Button — states", f'<div class="row">{states}</div><div class="row" style="margin-top:16px">{states2}</div>'))
    out.append(spec("Icon button and FAB", '<div class="row">'
                    + f'<button class="iconbtn" aria-label="More">{ic("more")}</button>'
                    + f'<button class="iconbtn iconbtn--tonal" aria-label="Edit">{ic("edit")}</button>'
                    + f'<button class="iconbtn iconbtn--filled" aria-label="Add">{ic("plus")}</button>'
                    + f'<button class="fab" aria-label="Create">{ic("plus")}</button>'
                    + '<span class="cap">all targets ≥ 48 × 48</span></div>'))
    out.append(spec("Text field — states", '<div class="col">'
                    + field("Default", "Placeholder", lead="mail")
                    + field("Focused", "", "Typing…", state="focus", helper="Helper text explains the format")
                    + field("Error", "", "not-an-email", state="error", helper="Enter a valid email address", trail="alert")
                    + field("Disabled", "", "Read only", state="disabled") + "</div>"))
    out.append(spec("Checkbox · Radio · Switch", '<div class="row" style="gap:24px">'
                    '<div class="col" style="gap:0">'
                    '<label class="check t-bodyLarge"><input type="checkbox" checked>Checked</label>'
                    '<label class="check t-bodyLarge"><input type="checkbox">Unchecked</label>'
                    '<label class="check t-bodyLarge"><input type="checkbox" disabled>Disabled</label></div>'
                    '<div class="col" style="gap:0">'
                    '<label class="check t-bodyLarge"><input type="radio" name="r1" checked>Option A</label>'
                    '<label class="check t-bodyLarge"><input type="radio" name="r1">Option B</label>'
                    '<label class="check t-bodyLarge"><input type="radio" name="r1" disabled>Disabled</label></div>'
                    '<div class="col" style="gap:0">'
                    '<label class="switch" aria-label="On"><input type="checkbox" role="switch" checked></label>'
                    '<label class="switch" aria-label="Off"><input type="checkbox" role="switch"></label>'
                    '<label class="switch" aria-label="Disabled"><input type="checkbox" role="switch" disabled></label></div></div>'))
    chips = (f'<button class="chip t-labelLarge" data-toggle>Assist</button>'
             f'<button class="chip is-selected t-labelLarge" data-toggle>{ic("check", 16)}Selected</button>'
             f'<button class="chip t-labelLarge">Input {ic("x", 16)}</button>'
             f'<span class="chip chip--tertiary t-labelLarge">{ic("star", 16)}Featured</span>')
    badges = (f'<span class="badge">3</span><span class="badge">99+</span><span class="badge badge--dot" aria-label="New"></span>'
              + status("success", "Success") + status("warning", "Warning") + status("error", "Error") + status("info", "Info")
              + status("neutral", "Neutral"))
    out.append(spec("Chip · Badge · Status", f'<div class="row">{chips}</div><div class="row" style="margin-top:16px">{badges}</div>'
                    '<p class="cap" style="margin-top:12px">Status never relies on color alone: icon + label are required.</p>'))
    avatars = ('<span class="avatar avatar--sm">AK</span><span class="avatar">AK</span><span class="avatar avatar--b">RM</span>'
               f'<span class="avatar avatar--c">{ic("user", 20)}</span><span class="avatar avatar--lg">AK</span>')
    out.append(spec("Avatar · Divider · Progress", f'<div class="row">{avatars}</div><hr class="divider" style="margin:20px 0">'
                    '<div class="col"><div class="progress" role="progressbar" aria-valuenow="64" aria-valuemin="0" aria-valuemax="100"><i style="width:64%"></i></div>'
                    '<div class="progress progress--ind" role="progressbar" aria-label="Loading"><i></i></div>'
                    '<div class="row"><span class="spinner spinner--lg" role="progressbar" aria-label="Loading"></span><span class="cap">linear determinate · indeterminate · circular</span></div></div>'))
    out.append(spec("Icons — 24px grid, 2px stroke, currentColor", '<div class="icons">' + "".join(
        f'<div title="{name}">{ic(name)}</div>' for name in ICONS if name not in ("moon", "sun")) + "</div>", "spec--full"))
    return '<div class="grid">' + "".join(out) + "</div>"


def _molecules_section() -> str:
    out = []
    out.append(spec("Search bar", f'<div class="searchbar">{ic("search", 20)}<input placeholder="Search" aria-label="Search">{ic("sliders", 20)}</div>'))
    out.append(spec("List tile", '<div style="margin:0 -16px">'
                    + tile("Single line", lead="inbox", trail=ic("chevron-right", 20))
                    + tile("Two lines", "Supporting text in one line", lead_html='<span class="avatar">AK</span>', trail='<span class="t-labelMedium">Now</span>')
                    + tile("With control", "Tap anywhere on the row", lead="bell", trail='<label class="switch" aria-label="Toggle"><input type="checkbox" role="switch" checked></label>')
                    + "</div>"))
    out.append(spec("Form field — label, helper, error", '<div class="col">'
                    + field("Email", "name@example.com", helper="We only use this to sign you in", lead="mail")
                    + field("Password", "", "123", state="error", helper="Use at least 8 characters", lead="lock", trail="eye", kind="password") + "</div>"))
    out.append(spec("Card header", '<div class="card"><div class="cardhead"><span class="avatar">AK</span><div class="cardhead__body">'
                    '<div class="t-titleMedium">Card title</div><div class="t-bodyMedium muted">Subtitle · 2h ago</div></div>'
                    f'<button class="iconbtn" aria-label="More">{ic("more")}</button></div></div>'))
    out.append(spec("Snackbar and inline banner", '<div class="col"><div class="snackbar t-bodyMedium" role="status"><span>Item archived</span><button class="t-labelLarge">Undo</button></div>'
                    f'<div class="banner banner--info t-bodyMedium" role="note">{ic("info", 20)}<span>Informational message with an icon and text.</span></div>'
                    f'<div class="banner banner--warning t-bodyMedium" role="note">{ic("alert", 20)}<span>Warning message — color is never the only cue.</span></div></div>'))
    seg = "".join(f'<button type="button" class="t-labelLarge{" is-selected" if i == 1 else ""}" aria-pressed="{"true" if i == 1 else "false"}">{ic("check", 16)}{lbl}</button>'
                  for i, lbl in enumerate(("Day", "Week", "Month")))
    out.append(spec("Segmented control", f'<div class="segmented" role="group" aria-label="Range">{seg}</div>'))
    return '<div class="grid">' + "".join(out) + "</div>"


def _organisms_section() -> str:
    out = []
    out.append(spec("App bar", '<div class="col" style="margin:0 -8px">' + appbar("Page title", actions=("search", "more"))
                    + '<hr class="divider">' + appbar("Section", lead="", actions=("bell",), style="t-headlineSmall") + "</div>"))
    out.append(spec("Bottom navigation", f'<div style="border-radius:var(--r-md);overflow:hidden">{navbar(0)}</div>'
                    '<p class="cap" style="margin-top:12px">3–5 destinations · active = pill + bold label (not color alone)</p>'))
    card = ('<div class="card"><div class="thumb" style="height:132px;border-radius:0">' + ic("image", 32) + '</div><div class="card__body">'
            '<div class="row between"><span class="t-titleMedium">Card title</span>' + status("success", "Active") + '</div>'
            '<p class="t-bodyMedium muted">Supporting text that describes the item in up to two lines of copy.</p></div>'
            '<div class="card__actions">' + btn("Dismiss", "text") + btn("Open", "filled", "sm") + "</div></div>")
    out.append(spec("Card", card))
    form = ('<div class="col">' + field("Full name", "Alex Kim") + field("Email", "name@example.com", lead="mail")
            + '<label class="check t-bodyMedium"><input type="checkbox" checked>Keep me updated</label>'
            + '<div class="row" style="justify-content:flex-end">' + btn("Cancel", "text") + btn("Save", "filled") + "</div></div>")
    out.append(spec("Form", form))
    listsec = ('<div class="card" style="background:var(--c-surface)"><div class="listsec__head"><span class="t-titleSmall">Section header</span>'
               '<a href="#organisms" class="t-labelLarge" style="text-decoration:none">See all</a></div>'
               + tile("First item", "Supporting text", lead="clock", trail=ic("chevron-right", 20)) + '<hr class="divider" style="margin-left:72px;width:auto">'
               + tile("Second item", "Supporting text", lead="calendar", trail=ic("chevron-right", 20)) + '<hr class="divider" style="margin-left:72px;width:auto">'
               + tile("Third item", "Supporting text", lead="bookmark", trail='<span class="badge">2</span>') + "</div>")
    out.append(spec("List section", listsec))
    dialog = ('<div class="scrimbox"><div class="dialog" role="alertdialog" aria-label="Delete item?"><div class="t-headlineSmall">Delete item?</div>'
              '<p class="t-bodyMedium muted">This cannot be undone. The item will be removed for everyone.</p>'
              '<div class="dialog__actions">' + btn("Cancel", "text") + btn("Delete", "danger-text") + "</div></div></div>")
    out.append(spec("Dialog", dialog))
    empty = (f'<div class="empty"><div class="empty__art">{ic("inbox", 40)}</div><div class="t-titleLarge">Nothing here yet</div>'
             '<p class="t-bodyMedium muted">When you add items they will show up here.</p>' + btn("Add item", "filled", icon="plus") + "</div>")
    out.append(spec("Empty state", empty))
    sheet = ('<div class="scrimbox" style="padding:24px 0 0;place-items:end stretch"><div class="sheet"><div class="sheet__grab"></div>'
             '<div class="t-titleLarge" style="margin-bottom:8px">Bottom sheet</div>'
             + tile("Share", lead="share") + tile("Save", lead="bookmark") + "</div></div>")
    out.append(spec("Bottom sheet", sheet))
    return '<div class="grid">' + "".join(out) + "</div>"


def _templates_section() -> str:
    def wf(name, note, blocks):
        return f'<div class="tpl"><div class="wf">{blocks}</div><b class="t-titleSmall">{name}</b><p>{note}</p></div>'

    items = [
        wf("Auth template", "Login, register, reset, OTP",
           '<div style="height:48px;border:0;background:transparent"></div><div style="height:54px;width:54px;align-self:center">Logo</div><div>Heading + lead</div>'
           '<div style="height:36px">Form field</div><div style="height:36px">Form field</div><div class="p" style="height:36px">Primary button</div>'
           '<div class="g" style="border:0;background:transparent"></div><div>Secondary link</div>'),
        wf("Dashboard template", "Home, overview, summary",
           '<div style="height:34px">App bar</div><div style="height:30px">Search bar</div><div class="p" style="height:76px">Hero / summary card</div>'
           '<div class="wfrow"><div style="height:56px">Stat</div><div style="height:56px">Stat</div></div><div class="g">List section</div><div style="height:38px">Bottom nav</div>'),
        wf("List template", "Search, browse, results, inbox",
           '<div style="height:34px">App bar</div><div style="height:30px">Search bar</div><div>Filter chips</div>'
           '<div class="g">List tiles<br>(or empty state)</div><div style="height:38px">Bottom nav</div>'),
        wf("Detail template", "Item, article, profile of a thing",
           '<div style="height:120px">Media header + back</div><div>Title + meta</div><div class="g">Content sections</div>'
           '<div class="wfrow"><div style="height:36px">Secondary</div><div class="p" style="height:36px">Primary</div></div>'),
        wf("Form template", "Create, edit, checkout step",
           '<div style="height:34px">App bar (close · title · save)</div><div style="height:36px">Form field</div><div style="height:36px">Form field</div>'
           '<div style="height:64px">Text area</div><div>Segmented / switch rows</div><div class="g" style="border:0;background:transparent"></div>'
           '<div class="p" style="height:36px">Sticky primary button</div>'),
        wf("Settings template", "Profile, preferences, account",
           '<div style="height:34px">App bar</div><div style="height:84px">Profile header</div><div class="g">List section</div><div class="g">List section</div>'
           '<div style="height:38px">Bottom nav</div>'),
    ]
    return '<div class="tpls">' + "".join(items) + "</div>"


def _pages_section(name: str) -> str:
    initial = e(name[:1].upper())
    pages = []

    # ---- login
    body = ('<div class="screen pad gap-lg" style="padding-top:40px">'
            f'<div class="mark" style="margin-bottom:8px">{initial}</div>'
            '<div><h3 class="t-headlineMedium">Welcome back</h3><p class="t-bodyLarge muted">Sign in to continue.</p></div>'
            + field("Email", "name@example.com", lead="mail", kind="email")
            + field("Password", "Your password", lead="lock", trail="eye", kind="password")
            + '<div class="row between"><label class="check t-bodyMedium"><input type="checkbox" checked>Remember me</label>'
            + btn("Forgot password?", "text") + "</div>"
            + btn("Log in", "filled", "lg", "btn--block")
            + '<div class="orline t-bodySmall">or</div>' + btn("Continue with SSO", "outlined", "lg", "btn--block", icon="shield")
            + '<div class="grow"></div><p class="t-bodyMedium center muted">New here? <a href="#pages" style="font-weight:700;text-decoration:none">Create account</a></p></div>')
    pages.append(phone("Login", "Auth template", body))

    # ---- register
    body = (appbar("", actions=()) + '<div class="screen pad gap-lg" style="padding-top:0">'
            '<div><h3 class="t-headlineMedium">Create account</h3><p class="t-bodyLarge muted">It takes less than a minute.</p></div>'
            + field("Full name", "Alex Kim", lead="user")
            + field("Email", "", "alex@", state="error", helper="Enter a valid email address", lead="mail")
            + field("Password", "", "••••••••••", helper="Strong password", lead="lock", trail="eye")
            + '<div class="progress" role="progressbar" aria-valuenow="80" aria-valuemin="0" aria-valuemax="100" style="margin-top:-8px"><i style="width:80%"></i></div>'
            + '<label class="check t-bodyMedium"><input type="checkbox">I agree to the Terms and Privacy Policy</label>'
            + '<div class="grow"></div>' + btn("Create account", "filled", "lg", "btn--block")
            + '<p class="t-bodyMedium center muted">Already have an account? <a href="#pages" style="font-weight:700;text-decoration:none">Log in</a></p></div>')
    pages.append(phone("Register", "Auth template · inline validation", body))

    # ---- home
    chips = "".join(f'<button class="chip t-labelLarge{" is-selected" if i == 0 else ""}" data-toggle>{lbl}</button>'
                    for i, lbl in enumerate(("All", "Recent", "Starred", "Shared", "Archived")))
    body = ('<header class="appbar appbar--pad"><div class="appbar__title" style="padding-left:0"><div class="t-bodyMedium muted">Good morning</div>'
            '<div class="t-titleLarge">Alex Kim</div></div>'
            f'<button class="iconbtn" aria-label="Notifications">{ic("bell")}<span class="badge badge--dot" style="position:absolute;top:10px;right:10px"></span></button>'
            '<span class="avatar">AK</span></header>'
            '<div class="screen gap-lg" style="padding-bottom:16px">'
            f'<div class="padx"><div class="searchbar">{ic("search", 20)}<input placeholder="Search" aria-label="Search"></div></div>'
            '<div class="padx"><div class="card card--filled"><div class="card__body" style="gap:12px">'
            '<div class="row between"><span class="t-labelLarge">Weekly summary</span>' + ic("trending", 20) + '</div>'
            '<div class="t-displaySmall">72%</div><div class="progress" style="background:color-mix(in srgb,var(--c-onPrimaryContainer) 16%,transparent)"><i style="width:72%"></i></div>'
            '<span class="t-bodyMedium">18 of 25 completed · 3 days left</span></div></div></div>'
            f'<div class="hscroll">{chips}</div>'
            '<div class="padx statgrid"><div class="stat"><span class="t-labelMedium muted">Active</span><span class="t-headlineSmall">12</span>' + status("success", "+3 today") + '</div>'
            '<div class="stat"><span class="t-labelMedium muted">Pending</span><span class="t-headlineSmall">5</span>' + status("warning", "2 due") + '</div></div>'
            '<div><div class="listsec__head" style="padding-top:0"><span class="t-titleMedium" style="color:var(--c-onSurface)">Recent</span>'
            '<a href="#pages" class="t-labelLarge" style="text-decoration:none">See all</a></div>'
            + tile("Item one", "Updated 2 minutes ago", lead_html=f'<span class="thumb" style="width:48px;height:48px">{ic("image", 20)}</span>', trail=ic("chevron-right", 20))
            + tile("Item two", "Updated yesterday", lead_html=f'<span class="thumb thumb--b" style="width:48px;height:48px">{ic("image", 20)}</span>', trail=ic("chevron-right", 20))
            + tile("Item three", "Updated last week", lead_html=f'<span class="thumb thumb--c" style="width:48px;height:48px">{ic("image", 20)}</span>', trail=ic("chevron-right", 20))
            + "</div></div>" + navbar(0))
    pages.append(phone("Home", "Dashboard template", body, f'<button class="fab fabpos" aria-label="Create">{ic("plus")}</button>'))

    # ---- list
    rows = [("Item title one", "Category · 2 min ago", "success", "Active", "thumb"),
            ("Item title two", "Category · 1 h ago", "warning", "Pending", "thumb thumb--b"),
            ("Item title three", "Category · Yesterday", "info", "New", "thumb thumb--c"),
            ("Item title four", "Category · 2 days ago", "error", "Failed", "thumb"),
            ("Item title five", "Category · Last week", "neutral", "Draft", "thumb thumb--b"),
            ("Item title six", "Category · Last week", "success", "Active", "thumb thumb--c"),
            ("Item title seven", "Category · 2 weeks ago", "neutral", "Draft", "thumb")]
    chips = "".join(f'<button class="chip t-labelLarge{" is-selected" if i == 0 else ""}" data-toggle>{ic("check", 16) if i == 0 else ""}{lbl}</button>'
                    for i, lbl in enumerate(("All", "Active", "Pending", "Draft", "Failed")))
    body = (appbar("Items", lead="", actions=("sliders", "more"), style="t-headlineSmall")
            + '<div class="screen gap-md">'
            f'<div class="padx"><div class="searchbar">{ic("search", 20)}<input placeholder="Search items" aria-label="Search items"></div></div>'
            f'<div class="hscroll">{chips}</div><div>'
            + '<hr class="divider">'.join(
                tile(t, s, lead_html=f'<span class="{cls}" style="width:48px;height:48px">{ic("image", 20)}</span>', trail=status(k, lbl))
                for t, s, k, lbl, cls in rows)
            + "</div></div>" + navbar(1))
    pages.append(phone("List", "List template", body))

    # ---- detail
    body = ('<div class="screen" style="position:relative">'
            '<div class="thumb" style="height:240px;border-radius:0;flex:none;position:relative">' + ic("image", 48)
            + f'<button class="iconbtn iconbtn--scrim" aria-label="Back" style="position:absolute;left:12px;top:12px">{ic("arrow-left")}</button>'
            f'<button class="iconbtn iconbtn--scrim" aria-label="Share" style="position:absolute;right:68px;top:12px">{ic("share")}</button>'
            f'<button class="iconbtn iconbtn--scrim" aria-label="Save" style="position:absolute;right:12px;top:12px">{ic("bookmark")}</button></div>'
            '<div class="pad col gap-lg">'
            '<div class="col gap-sm"><div class="row gap-sm">' + status("success", "Available")
            + f'<span class="chip chip--tertiary t-labelMedium" style="height:24px">{ic("star", 14)}4.8</span></div>'
            '<h3 class="t-headlineSmall">Item detail title that can wrap to two lines</h3>'
            '<p class="t-bodyMedium muted">Category · Updated 2 hours ago</p></div>'
            '<p class="t-bodyLarge">Body copy explains the item. It uses bodyLarge on the surface color with a comfortable line height, '
            'so long descriptions stay readable.</p>'
            '<div class="card"><div class="cardhead"><span class="avatar avatar--b">RM</span><div class="cardhead__body">'
            '<div class="t-titleMedium">Rina Maharani</div><div class="t-bodyMedium muted">Owner</div></div>' + btn("Message", "tonal", "sm") + '</div></div>'
            '<div><div class="t-titleMedium" style="margin-bottom:4px">Details</div>'
            '<div class="kv t-bodyMedium"><span class="muted">Reference</span><span class="mono">#A-10294</span></div>'
            '<div class="kv t-bodyMedium"><span class="muted">Created</span><span>12 Mar 2026</span></div>'
            '<div class="kv t-bodyMedium"><span class="muted">Location</span><span>Jakarta</span></div></div>'
            '</div></div><div class="bottombar">' + btn("Save", "outlined", "lg", icon="bookmark") + btn("Continue", "filled", "lg", "grow") + "</div>")
    pages.append(phone("Detail", "Detail template · sticky actions", body))

    # ---- form
    seg = "".join(f'<button type="button" class="t-labelLarge{" is-selected" if i == 1 else ""}" aria-pressed="{"true" if i == 1 else "false"}">{ic("check", 16)}{lbl}</button>'
                  for i, lbl in enumerate(("Low", "Medium", "High")))
    body = ('<header class="appbar"><button class="iconbtn" aria-label="Close">' + ic("x") + '</button>'
            '<div class="appbar__title t-titleLarge">New item</div>' + btn("Save", "text") + '</header>'
            '<div class="screen pad gap-lg" style="padding-top:8px">'
            + field("Title", "Give it a name", "Quarterly review")
            + field("Category", "", "General", trail="chevron-down")
            + field("Date", "", "12 Mar 2026", trail="calendar")
            + '<div class="field"><span class="field__label t-labelLarge">Priority</span><div class="segmented" role="group" aria-label="Priority">' + seg + '</div></div>'
            + field("Description", "Add more detail", area=True, helper="Optional · 0/280")
            + '<div class="card" style="background:var(--c-surface)">'
            + tile("Notify me", "Send a reminder one day before", lead="bell", trail='<label class="switch" aria-label="Notify me"><input type="checkbox" role="switch" checked></label>')
            + '</div></div><div class="bottombar">' + btn("Create item", "filled", "lg", "grow") + "</div>")
    pages.append(phone("Form", "Form template", body))

    # ---- profile
    body = (appbar("Profile", lead="", actions=("sliders",), style="t-headlineSmall")
            + '<div class="screen gap-md">'
            '<div class="pad col gap-md" style="align-items:center;text-align:center">'
            '<span class="avatar avatar--lg">AK</span><div><div class="t-titleLarge">Alex Kim</div><div class="t-bodyMedium muted">alex.kim@example.com</div></div>'
            + btn("Edit profile", "tonal", "sm", icon="edit") + "</div>"
            '<div><div class="listsec__head" style="padding-top:0"><span class="t-titleSmall">Account</span></div>'
            + tile("Personal information", lead="user", trail=ic("chevron-right", 20))
            + tile("Security", "Password, biometrics", lead="shield", trail=ic("chevron-right", 20))
            + tile("Notifications", lead="bell", trail='<span class="badge">3</span>' + ic("chevron-right", 20))
            + '</div><hr class="divider"><div><div class="listsec__head"><span class="t-titleSmall">Preferences</span></div>'
            + tile("Language", "English", lead="globe", trail=ic("chevron-right", 20))
            + tile("Dark mode", lead="moon", trail='<label class="switch" aria-label="Dark mode"><input type="checkbox" role="switch"></label>')
            + tile("Help and support", lead="help", trail=ic("chevron-right", 20))
            + '</div><div class="padx" style="padding-bottom:16px">' + btn("Log out", "danger-text", "", "btn--block", icon="logout") + "</div></div>" + navbar(3))
    pages.append(phone("Profile / Settings", "Settings template", body))
    return '<div class="phones">' + "".join(pages) + "</div>"


def _rationale_section(info: dict) -> str:
    rationale = info.get("rationale") or {}
    cards = "".join(
        f'<div><h4>{title}</h4><p class="t-bodyMedium muted">{e(rationale[key])}</p></div>'
        for key, title in (("color", "Color"), ("typography", "Typography"), ("shape", "Shape and density"), ("motion", "Motion"))
        if rationale.get(key))
    parts = []
    if info.get("audience"):
        parts.append(spec("Audience", f'<p class="t-bodyLarge">{e(info["audience"])}</p>', "spec--full"))
    if cards:
        parts.append(spec("Why it looks like this", f'<div class="rationale">{cards}</div>', "spec--full"))
    if info.get("do") or info.get("dont"):
        do = "".join(f'<li>{ic("check-circle", 20)}<span>{e(item)}</span></li>' for item in info.get("do", []))
        dont = "".join(f'<li>{ic("x-circle", 20)}<span>{e(item)}</span></li>' for item in info.get("dont", []))
        parts.append(spec("Do / Don't", f'<div class="dodont"><ul class="do">{do}</ul><ul class="dont">{dont}</ul></div>', "spec--full"))
    return '<div class="grid">' + "".join(parts) + "</div>" if parts else ""


# --------------------------------------------------------------------------- page


def build_id(tokens_text: str) -> str:
    return f"{RENDERER_VERSION}-{L.sha(tokens_text)}"


def render(tokens: dict, source: str = "builtin", tokens_text: str | None = None) -> str:
    info = L.meta(tokens)
    spec_ = info.get("spec") or {}
    name = info.get("name", info.get("id", "Design system"))
    fonts = info.get("fonts", {})
    font_url = L.google_fonts_url([fonts.get("display", "Inter"), fonts.get("body", "Inter"), fonts.get("mono", "JetBrains Mono")])
    tokens_text = tokens_text if tokens_text is not None else json.dumps(tokens, sort_keys=True)
    swatch = "".join(f'<i style="background:var(--c-{role})" title="{role}"></i>'
                     for role in ("primary", "secondary", "tertiary", "primaryContainer", "surfaceContainerHigh", "inverseSurface"))
    tags = [("ID", info.get("id", "")), ("Source", source), ("Context", info.get("context", "")),
            ("Personality", ", ".join(info.get("personality", []))),
            ("Shape", spec_.get("corner", "")), ("Density", spec_.get("density", "")), ("Motion", spec_.get("motion", "")),
            ("Contrast", "WCAG 2.2 " + spec_.get("contrast", "AA"))]
    if info.get("base"):
        tags.insert(2, ("Based on", info["base"]))
    tags_html = "".join(f'<span class="tag">{e(k)} <b>{e(v)}</b></span>' for k, v in tags if v)
    nav = [("overview", "Overview"), ("tokens", "Tokens"), ("atoms", "Atoms"), ("molecules", "Molecules"),
           ("organisms", "Organisms"), ("templates", "Templates"), ("pages", "Pages")]
    nav_html = "".join(f'<a href="#{a}">{t}</a>' for a, t in nav)
    atomic = '<div class="atomic">' + "<i>→</i>".join(f"<span>{t}</span>" for _, t in nav[1:]) + "</div>"
    letter = info.get("letter") or name[:1].upper()

    body = [
        f'<header class="hero"><div class="wrap"><div class="hero__row"><div><div class="hero__id"><div class="mark">{e(letter)}</div>'
        f'<div><div class="t-labelLarge muted">designku design system</div><h1 class="t-displaySmall">{e(name)}</h1></div></div>'
        f'<p class="lead t-titleLarge" style="color:var(--c-onSurface)">{e(info.get("tagline", ""))}</p>'
        f'<div class="hero__meta">{tags_html}</div></div><div class="hero__swatch" aria-hidden="true">{swatch}</div></div></div></header>',
        f'<nav class="topnav" aria-label="Sections"><div class="wrap topnav__row"><span class="topnav__name">{e(name)}</span>'
        f'<div class="topnav__links">{nav_html}</div>'
        f'<button id="themeBtn" type="button" class="btn btn--outlined btn--sm t-labelLarge" aria-pressed="false" title="Toggle theme (D)">'
        f'<span class="only-light">{ic("sun", 18)}</span><span class="only-dark">{ic("moon", 18)}</span><span class="lbl">Light</span></button></div></nav>',
        "<main>",
        section("overview", "Overview", "Design rationale",
                "Who this system is for and the reasoning behind each decision. Agents must use these tokens and components — "
                "never guess a color, font, spacing or radius." + atomic, _rationale_section(info)),
        section("tokens", "Level 0", "Core tokens",
                "The single source of truth (<span class='mono'>tokens.json</span>, W3C DTCG). Primitives feed semantic roles; UI code only ever references semantic roles.",
                _tokens_section(tokens)),
        section("atoms", "Level 1", "Atoms", "Smallest usable pieces. They consume tokens only and carry all states.", _atoms_section()),
        section("molecules", "Level 2", "Molecules", "Small groups of atoms that do one job.", _molecules_section()),
        section("organisms", "Level 3", "Organisms", "Self-contained regions of a screen built from molecules and atoms.", _organisms_section()),
        section("templates", "Level 4", "Templates", "Page skeletons: which organisms go where. No real content, no business logic.", _templates_section()),
        section("pages", "Level 5", "Pages",
                "Templates filled with generic content to show the system in use. Scroll sideways; each phone scrolls on its own.",
                _pages_section(name)),
        "</main>",
        f'<footer class="foot"><div class="wrap">Generated by designku from <span class="mono">tokens.json</span> · {e(info.get("id", ""))} · '
        f'renderer v{RENDERER_VERSION} · press <b>D</b> to toggle light/dark</div></footer>',
    ]
    return (f'<!DOCTYPE html>\n<html lang="en" data-theme="light">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta name="designku-build" content="{build_id(tokens_text)}">\n'
            f'<title>{e(name)} — designku design system</title>\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{e(font_url)}">\n'
            f'<style>\n{css_variables(tokens)}\n{BASE_CSS}</style>\n</head>\n<body>\n' + "\n".join(body)
            + f"\n<script>{SCRIPT}</script>\n</body>\n</html>\n")


def preview_is_fresh(path: Path, tokens_text: str) -> bool:
    if not path.is_file():
        return False
    try:
        with open(path, "r", encoding="utf-8") as fh:
            head = fh.read(1024)
    except OSError:
        return False
    return f'content="{build_id(tokens_text)}"' in head


def ensure_preview(system: dict, force: bool = False) -> tuple[Path, bool]:
    """Render preview.html next to tokens.json if missing/stale. Returns (path, regenerated).

    If the system folder is read-only (installed plugin cache), fall back to
    ~/.designku/cache/previews/<id>.html.
    """
    tokens_text = Path(system["tokens_path"]).read_text(encoding="utf-8")
    primary = Path(system["dir"]) / "preview.html"
    fallback = L.user_home() / "cache" / "previews" / f"{system['id']}.html"
    for candidate in (primary, fallback):
        if not force and preview_is_fresh(candidate, tokens_text):
            return candidate, False
    page = render(system["tokens"], system["source"], tokens_text)
    for candidate in (primary, fallback):
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(page, encoding="utf-8")
            return candidate, True
        except OSError:
            continue
    raise OSError(f"cannot write preview for {system['id']}")
