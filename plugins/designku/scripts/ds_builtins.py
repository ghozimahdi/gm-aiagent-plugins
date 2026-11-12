#!/usr/bin/env python3
"""Maintainer tool: (re)build the built-in catalog under plugins/designku/systems/.

Each entry is a compact spec + UX rationale. `python3 ds_builtins.py` rewrites
tokens.json and README.md for all of them; previews are rendered by
`designku.py preview --all`. End users never run this file.
"""
from __future__ import annotations

import sys

import dslib as L
import ds_engine
import ds_validate

BUILTINS = [
    {
        "meta": {
            "id": "aegis", "name": "Aegis", "letter": "A", "group": "business",
            "context": "Fintech, banking, insurance, payments",
            "tagline": "Calm authority for money and sensitive data.",
            "audience": "Adults 22-55 moving their own money; anxious about mistakes, scanning numbers on the go, often outdoors in bright light.",
            "personality": ["trustworthy", "precise", "composed", "premium"],
            "rationale": {
                "color": "Deep cobalt blue is the most consistently trust-associated hue across markets and stays legible in sunlight. A desaturated blue-slate secondary keeps dense screens quiet, and a restrained gold tertiary marks rewards and premium tiers without competing with the primary call to action. Neutrals carry a faint blue tint so greys never look dirty next to the brand color.",
                "typography": "Manrope headlines have open, unambiguous numerals (critical for balances and amounts). Public Sans body text is plain and institutional, which reads as honest rather than promotional.",
                "shape": "Rounded 12-16px corners soften a serious palette just enough to feel modern, not bureaucratic. Comfortable density with 48px controls because a mis-tap on a transfer is expensive.",
                "motion": "Balanced, never bouncy. Money movements should feel deliberate; confirmation states get the slow duration so users notice them.",
            },
            "do": [
                "Use primary only for the single most important action per screen (Pay, Transfer, Confirm).",
                "Show amounts in titleLarge or larger; use the mono family for account numbers and tabular figures.",
                "Pair every success/error state with an icon and plain-language text (\"Transfer sent\"), not color alone.",
            ],
            "dont": [
                "Do not use the gold tertiary for buttons or errors — it is a reward/premium accent only.",
                "Do not color negative amounts with error red unless the value is an actual problem; use onSurface with a minus sign.",
                "Do not stack more than one filled button in a view.",
            ],
        },
        "spec": {
            "primary": "#1447C4", "secondary": "#4E6480", "tertiary": "#A8791A",
            "neutralChroma": 0.008, "mood": "professional",
            "fonts": {"display": "Manrope", "body": "Public Sans", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 700, "headlineWeight": 700, "titleWeight": 600, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -1.0},
            "corner": "rounded", "density": "comfortable", "motion": "balanced", "elevation": "soft",
        },
    },
    {
        "meta": {
            "id": "serene", "name": "Serene", "letter": "B", "group": "wellbeing",
            "context": "Health, wellness, telemedicine, mental health, habit tracking",
            "tagline": "Low-arousal and reassuring, for people who may already be stressed.",
            "audience": "Patients and self-carers of all ages, including older adults and people using the app while unwell, tired or worried.",
            "personality": ["calm", "caring", "clear", "unhurried"],
            "rationale": {
                "color": "A muted sage-teal sits between blue (clinical trust) and green (health, growth) and has low arousal, which lowers perceived urgency. The warm clay tertiary adds human warmth so the product does not feel like a hospital. Saturation is deliberately capped; the only loud color on screen should be a genuine alert.",
                "typography": "Outfit headlines are soft and geometric; Figtree body text has open apertures and generous spacing that hold up for older eyes and at larger dynamic type sizes.",
                "shape": "Pill buttons and large radii read as gentle and safe. Spacious layout reduces cognitive load when the user is not at their best.",
                "motion": "Balanced timing with standard easing — slow enough to feel calm, never animated for decoration.",
            },
            "do": [
                "Lead with one clear next step per screen; keep secondary actions as text buttons.",
                "Use the container tones (primaryContainer, tertiaryContainer) for large calm areas instead of solid primary.",
                "Reserve error for clinically important alerts and always explain what to do next.",
            ],
            "dont": [
                "Do not use red for routine things such as an incomplete habit or a missed streak — it induces guilt.",
                "Do not shrink body text below bodyMedium; many users will have their system font size raised.",
                "Do not use countdown timers, badges or urgency patterns.",
            ],
        },
        "spec": {
            "primary": "#2B7A6B", "secondary": "#4F7A70", "tertiary": "#B4674A",
            "neutralChroma": 0.010, "mood": "calm",
            "fonts": {"display": "Outfit", "body": "Figtree", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 500, "headlineWeight": 600, "titleWeight": 600, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -0.5},
            "corner": "pill", "density": "spacious", "motion": "balanced", "elevation": "flat",
        },
    },
    {
        "meta": {
            "id": "bazaar", "name": "Bazaar", "letter": "C", "group": "commerce",
            "context": "E-commerce, marketplace, retail, deals",
            "tagline": "High-energy and conversion-focused without shouting.",
            "audience": "Deal-seeking shoppers browsing fast with one thumb, comparing many items, often on mid-range Android devices.",
            "personality": ["energetic", "direct", "generous", "dependable"],
            "rationale": {
                "color": "A hot orange-red primary draws the eye to Buy and Add-to-cart; warm hues raise arousal and are the convention shoppers already know from major marketplaces. It is darkened to tone 45 so white button labels pass AA (most marketplace oranges do not). The secondary is a muted terracotta in the same hue family, so selected chips, tabs and tonal buttons read as part of the brand instead of introducing a second color; a bright yellow tertiary is the only accent, reserved for promos and ratings. Neutrals are a warm sand so greys never look cold next to the orange. Error is shifted to crimson so it can never be confused with the red-orange CTA, and it always carries an icon.",
                "typography": "Plus Jakarta Sans throughout: friendly, compact, and its bold weights keep prices punchy at small sizes.",
                "shape": "Soft 8-12px corners maximize the image area on product cards. Comfortable density keeps the buy button a full 48px.",
                "motion": "Snappy (80% durations) — browsing should feel fast; add-to-cart feedback is immediate.",
            },
            "do": [
                "Keep exactly one filled primary button visible in the sticky bottom bar (Add to cart / Buy now).",
                "Show price in titleLarge with strong weight; strike-through prices use onSurfaceVariant.",
                "Use tertiaryContainer for promo chips and star ratings.",
            ],
            "dont": [
                "Do not use primary for discounts and errors at the same time — discount badges use tertiary, failures use error.",
                "Do not put primary-colored text on surfaceContainerHigh/Highest (contrast drops below AA for text).",
                "Do not animate every card; motion budget goes to cart and checkout feedback.",
            ],
        },
        "spec": {
            "primary": "#F4511E", "secondary": "#A8623F", "tertiary": "#E0A800",
            "error": "#B0125A", "neutralChroma": 0.012, "neutralHue": 60, "mood": "vibrant",
            "fonts": {"display": "Plus Jakarta Sans", "body": "Plus Jakarta Sans", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 700, "headlineWeight": 700, "titleWeight": 700, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -0.8},
            "corner": "soft", "density": "comfortable", "motion": "snappy", "elevation": "soft",
            "tones": {"light": {"primary": 45}},
        },
    },
    {
        "meta": {
            "id": "focus", "name": "Focus", "letter": "D", "group": "business",
            "context": "Productivity, tasks, notes, project tools, SaaS",
            "tagline": "Quiet chrome so the user's content is the interface.",
            "audience": "Knowledge workers in long sessions who return many times a day and value speed and keyboard-like efficiency.",
            "personality": ["focused", "efficient", "modern", "unobtrusive"],
            "rationale": {
                "color": "Indigo is distinctive yet recedes behind content, and reads as 'tool' rather than 'brand campaign'. Secondary is a true slate grey so most of the UI is near-monochrome; the teal tertiary is used sparingly for tags and progress. Low neutral chroma keeps long reading sessions free of color cast.",
                "typography": "Inter everywhere: purpose-built for UI, excellent at 12-14px, with tabular numerals for dates and counts.",
                "shape": "Soft 8-12px radii and compact density (40px buttons, 56px rows) fit more information per screen while each row keeps a 48px+ touch target.",
                "motion": "Snappy. Frequent actions (check off, archive) must feel instant; nothing lasts beyond 240ms except full-screen transitions.",
            },
            "do": [
                "Use surface containers and dividers to build hierarchy before reaching for color.",
                "Use primary for the current selection and the single create action (FAB or app-bar button).",
                "Keep list rows scannable: titleSmall + bodySmall, one trailing meta item.",
            ],
            "dont": [
                "Do not color-code more than five categories; add an icon or label to every tag color.",
                "Do not use display styles inside task lists — headlineSmall is the practical maximum.",
                "Do not add shadows to list items; elevation is for overlays only.",
            ],
        },
        "spec": {
            "primary": "#4F46E5", "secondary": "#5B6577", "tertiary": "#0E8A7D",
            "neutralChroma": 0.005, "mood": "professional",
            "fonts": {"display": "Inter", "body": "Inter", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 600, "headlineWeight": 600, "titleWeight": 600, "labelWeight": 500, "bodyWeight": 400, "displayTracking": -1.2},
            "corner": "soft", "density": "compact", "motion": "snappy", "elevation": "flat",
        },
    },
    {
        "meta": {
            "id": "sprout", "name": "Sprout", "letter": "E", "group": "wellbeing",
            "context": "Education, kids and family, language learning, gamified habits",
            "tagline": "Playful and encouraging, with big targets for small (or distracted) hands.",
            "audience": "Children 6-12 with a parent nearby, and casual adult learners doing five-minute sessions; developing readers and imprecise motor control.",
            "personality": ["playful", "encouraging", "bright", "safe"],
            "rationale": {
                "color": "Leaf green signals growth and 'correct', and is gender-neutral for children. A softer leaf-green secondary keeps selection and tonal states in the brand family, and a sunshine yellow tertiary supplies the playful accent for stars, streaks and rewards. Because green doubles as success, wrong answers use an error container with an icon and a gentle message rather than a red screen.",
                "typography": "Baloo 2 headlines are chunky and friendly. Nunito body has rounded terminals and clearly distinct letterforms (a, g, l, I), which helps early readers.",
                "shape": "Rounded 16-24px corners and spacious density: 52px buttons and 72px list rows forgive imprecise taps.",
                "motion": "Expressive: 120% durations and an overshoot curve on the emphasized easing make rewards feel alive. Always respect reduce-motion.",
            },
            "do": [
                "Celebrate progress with tertiary (stars, streaks) and primary (correct, continue).",
                "Use icons plus words on every button; never rely on reading alone or color alone.",
                "Keep one task per screen with a large primary button anchored at the bottom.",
            ],
            "dont": [
                "Do not punish with red full-screen states; use errorContainer and an encouraging retry.",
                "Do not go below bodyLarge for instructions aimed at children.",
                "Do not place destructive or purchase actions near the primary button.",
            ],
        },
        "spec": {
            "primary": "#3A8F1E", "secondary": "#5E8A3C", "tertiary": "#D9A300",
            "neutralChroma": 0.012, "neutralHue": 110, "mood": "playful",
            "fonts": {"display": "Baloo 2", "body": "Nunito", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 700, "headlineWeight": 700, "titleWeight": 700, "labelWeight": 700, "bodyWeight": 500, "displayTracking": -0.3},
            "corner": "rounded", "density": "spacious", "motion": "expressive", "elevation": "lifted",
        },
    },
    {
        "meta": {
            "id": "kopi", "name": "Kopi", "letter": "F", "group": "commerce",
            "context": "Food and beverage, cafes, restaurants, travel, lifestyle, hospitality",
            "tagline": "Warm, tactile and appetizing — a menu, not a dashboard.",
            "audience": "Customers ordering or browsing at leisure; emotional, sensory decisions driven by photography.",
            "personality": ["warm", "crafted", "inviting", "unpretentious"],
            "rationale": {
                "color": "Roasted-coffee brown is earthy and appetizing and, unlike saturated red or orange, never fights with food photography. A muted latte secondary keeps selected and tonal states inside the coffee family; caramel-saffron tertiary highlights specials. Neutrals are a warm cream (higher chroma, hue 75) instead of clinical white, like paper or linen.",
                "typography": "Fraunces, a soft old-style serif, gives headlines the feel of a printed menu. DM Sans body keeps prices and options clean and modern.",
                "shape": "Soft 8-16px corners, comfortable density. Cards are image-first with generous padding.",
                "motion": "Balanced and gentle; image fades and sheet transitions use the slow duration.",
            },
            "do": [
                "Let photography carry the color; keep chrome on cream surfaces.",
                "Use headline styles (serif) for dish and place names, body (sans) for descriptions and prices.",
                "Use tertiaryContainer for 'new' and 'chef's pick' labels.",
            ],
            "dont": [
                "Do not set long paragraphs in the serif display family — it is for headlines only.",
                "Do not place text directly on photos without a scrim.",
                "Do not use pure white cards; surfaceContainerLowest is the brightest surface and should be used sparingly.",
            ],
        },
        "spec": {
            "primary": "#7A4B2A", "secondary": "#8A6A52", "tertiary": "#C27A1A",
            "error": "#B3123F", "neutralChroma": 0.014, "neutralHue": 75, "mood": "warm",
            "fonts": {"display": "Fraunces", "body": "DM Sans", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 600, "headlineWeight": 600, "titleWeight": 600, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -0.6},
            "corner": "soft", "density": "comfortable", "motion": "balanced", "elevation": "soft",
        },
    },
    {
        "meta": {
            "id": "pulse", "name": "Pulse", "letter": "G", "group": "commerce",
            "context": "Social, community, creator tools, entertainment, events, dating",
            "tagline": "Vibrant and expressive, built dark-first for media.",
            "audience": "Gen Z and young millennials in short, frequent, often night-time sessions; content is user-generated photo and video.",
            "personality": ["bold", "expressive", "youthful", "immersive"],
            "rationale": {
                "color": "Electric magenta is high-arousal and ownable in a category crowded with blue. A dusty orchid secondary keeps selection states in the magenta family, and a violet tertiary is the analogous accent for stories, reactions and live states. Dark mode uses a near-black tinted surface (the one context where it is appropriate) so media pops and OLED screens save power — but never pure #000, which smears when scrolling.",
                "typography": "Sora headlines are wide and confident; Be Vietnam Pro body text stays readable in dense comment threads.",
                "shape": "Pill buttons and chips, large card radii — everything feels tappable and soft. Comfortable density.",
                "motion": "Expressive: overshoot on likes and reactions; 120% durations. Always respect reduce-motion.",
            },
            "do": [
                "Design dark-first and verify light mode second.",
                "Use primary for the main social action (Post, Follow) and for active nav state.",
                "Use gradients only between adjacent tonal steps of one palette if at all.",
            ],
            "dont": [
                "Do not place magenta text on photos or video without a scrim.",
                "Do not use primary and error side by side (hues are 40° apart) — destructive actions need an icon and a confirmation.",
                "Do not use all three accent colors on one component.",
            ],
        },
        "spec": {
            "primary": "#C2189B", "secondary": "#A0478C", "tertiary": "#6D4BD8",
            "error": "#C62810", "neutralChroma": 0.010, "mood": "vibrant",
            "fonts": {"display": "Sora", "body": "Be Vietnam Pro", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 700, "headlineWeight": 700, "titleWeight": 600, "labelWeight": 600, "bodyWeight": 400, "displayTracking": -1.2},
            "corner": "pill", "density": "comfortable", "motion": "expressive", "elevation": "flat",
            "darkStyle": "oled",
        },
    },
    {
        "meta": {
            "id": "slate", "name": "Slate", "letter": "H", "group": "business",
            "context": "Enterprise, B2B, admin, internal tools, white-label base",
            "tagline": "Neutral monochrome that disappears behind data — and behind any brand.",
            "audience": "Professionals using dense, data-heavy screens under time pressure; also teams who need a neutral base to re-skin per client.",
            "personality": ["neutral", "rigorous", "dense", "durable"],
            "rationale": {
                "color": "A graphite near-black primary gives maximum contrast and zero brand bias, so status colors and charts carry all the meaning. A single blue tertiary is kept for links, focus and selection. This is also the safest starting point for /designku:ds-customize.",
                "typography": "IBM Plex Sans has an engineered, technical voice with distinct glyphs for I, l and 1; IBM Plex Mono for IDs and codes.",
                "shape": "Sharp 4-8px corners and compact density read as professional tooling and maximize data per screen.",
                "motion": "Snappy and functional only.",
            },
            "do": [
                "Use tertiary (blue) for links, focus rings and selected rows; primary (graphite) for the main button.",
                "Encode status with color + icon + label; this system is designed for many status chips.",
                "Use the mono family for identifiers, codes and aligned numeric columns.",
            ],
            "dont": [
                "Do not introduce new accent colors per feature; extend tokens.json if a category color is truly needed.",
                "Do not use elevation for static cards — use outlineVariant borders.",
                "Do not reduce row height below size.listItem to fit more data.",
            ],
        },
        "spec": {
            "primary": "#2C3440", "secondary": "#56606E", "tertiary": "#1D5FD1",
            "neutralChroma": 0.004, "mood": "professional",
            "fonts": {"display": "IBM Plex Sans", "body": "IBM Plex Sans", "mono": "IBM Plex Mono"},
            "type": {"displayWeight": 600, "headlineWeight": 600, "titleWeight": 600, "labelWeight": 500, "bodyWeight": 400, "displayTracking": -0.8},
            "corner": "sharp", "density": "compact", "motion": "snappy", "elevation": "flat",
            "tones": {"light": {"primary": 20}, "dark": {"primary": 90}},
        },
    },
    {
        "meta": {
            "id": "tinta", "name": "Tinta", "letter": "I", "group": "business",
            "context": "Creator tools, content and video editing, indie SaaS, startups",
            "tagline": "Neo-brutalism: ink outlines and hard offset shadows on warm paper, bold but still accessible.",
            "audience": "Creators, marketers and small teams who want a tool that feels confident and hand-made rather than corporate, and who return to it daily to make things.",
            "personality": ["bold", "honest", "playful", "crafted"],
            "rationale": {
                "color": "Ported from the Cuplikin app. A saturated electric blue primary on an off-white, faintly green 'paper' background, with deep navy 'ink' for text, outlines and shadows instead of pure black, which keeps the brutalist contrast but softens it. Pastel mint, sky, peach and lavender containers act like highlighter marks for tags, credits and status, and the blue stays the only saturated color on screen. Dark mode switches to calm zinc greys and drops the hard shadow, because a light offset shadow on a dark surface looks like a rendering glitch.",
                "typography": "Jost headlines (geometric, Futura-like, with a poster feel) pair with Mulish body text, which stays highly legible at small sizes in dense editor UIs.",
                "shape": "Neo-brutalism: primary buttons, the FAB, elevated cards and dialogs get a 1.5px ink outline and a 3px hard shadow with zero blur. Pressing a button moves it into its shadow, so it feels physically pushed. Medium radii (12-16px) keep it friendly rather than raw. Everyday surfaces follow the app: cards, list groups, the search field and the bottom navigation are white with a 1px light line on the paper background (no grey fills), list thumbnails are solid pastel tiles, and chips are pills with a thin line. Secondary buttons, cards and inputs stay flat, so the raised treatment always marks the one thing to press.",
                "motion": "Snappy. The press-into-shadow translate is the main motion; everything else stays short.",
            },
            "do": [
                "Give the hard shadow only to the single primary action per region (DsButton filled/danger, FAB) and to elevated cards or dialogs; everything else stays flat with thin borders.",
                "Use the pastel containers (primaryContainer = sky, tertiaryContainer = mint, warningContainer = peach) for badges, tags and credit or status chips.",
                "Keep text and outlines in onSurface (ink); never use pure black.",
            ],
            "dont": [
                "Do not hand-draw BoxShadow or borders in feature code. DsEffect and the Ds* atoms already apply the outline and hard shadow, and switch them off in dark mode.",
                "Do not stack several raised (shadowed) elements next to each other; neo-brutalism loses hierarchy when everything pops.",
                "Do not add blur to the shadow or color it with the brand blue; it is always a zero-blur ink offset.",
            ],
        },
        "spec": {
            "primary": "#1460ED", "secondary": "#4A6390", "tertiary": "#5E8C1E",
            "error": "#B43C30", "success": "#48723B", "warning": "#A45A0C",
            "neutralHue": 114, "neutralChroma": 0.010, "mood": "playful",
            "fonts": {"display": "Jost", "body": "Mulish", "mono": "JetBrains Mono"},
            "type": {"displayWeight": 600, "headlineWeight": 600, "titleWeight": 700, "labelWeight": 700, "bodyWeight": 400, "displayTracking": -0.6},
            "corner": "soft", "density": "comfortable", "motion": "snappy", "elevation": "flat",
            "style": "brutal",
            "overrides": {
                "light": {
                    "primary": "#1460ED", "onPrimary": "#FFFFFF",
                    "primaryContainer": "#E8F1FF", "secondaryContainer": "#E8F1FF",
                    "tertiaryContainer": "#D3F7AC", "onTertiaryContainer": "#1D4B19",
                    "warningContainer": "#FFD2B2", "onWarningContainer": "#6B3A14",
                    "errorContainer": "#FBE6E2",
                    "background": "#F8F9F3", "surface": "#F8F9F3", "surfaceBright": "#F8F9F3",
                    "surfaceContainerLowest": "#FFFFFF", "surfaceContainerLow": "#FFFFFF",
                    "surfaceContainer": "#FFFFFF", "surfaceContainerHigh": "#F0F2E9",
                    "surfaceContainerHighest": "#E5E8E0", "surfaceVariant": "#EEF1E7",
                    "onSecondaryContainer": "#1460ED",
                    "onBackground": "#192C42", "onSurface": "#192C42", "onSurfaceVariant": "#526174",
                    "outlineVariant": "#DCE1D9", "inverseSurface": "#192C42",
                },
                "dark": {
                    "background": "#141416", "surface": "#141416", "surfaceDim": "#141416",
                    "surfaceContainerLowest": "#0D0D0F", "surfaceContainerLow": "#1C1C1F",
                    "surfaceContainer": "#1C1C1F", "surfaceContainerHigh": "#28282C",
                    "surfaceContainerHighest": "#323237",
                    "onBackground": "#EDEDF0", "onSurface": "#EDEDF0", "onSurfaceVariant": "#A1A1AA",
                    "outlineVariant": "#303034", "surfaceVariant": "#28282C", "outline": "#8E8E96",
                    "primaryContainer": "#263249", "secondaryContainer": "#263249",
                    "tertiaryContainer": "#29352D", "warningContainer": "#3B302A", "errorContainer": "#3A2724",
                },
            },
        },
    },
]


def readme(tokens: dict) -> str:
    """Render the rationale README.md for a system (built-in or custom)."""
    info = L.meta(tokens)
    spec = info.get("spec", {})
    rationale = info.get("rationale", {})
    stats = ds_validate.summary(tokens)

    def color(mode, role):
        return L.tv(tokens, f"color.{mode}.{role}")

    lines = [
        f"# {info.get('name')}" + (f" ({info['letter']})" if info.get("letter") else ""),
        "",
        f"> {info.get('tagline', '')}",
        "",
        f"- **ID:** `{info.get('id')}`",
        f"- **Context:** {info.get('context', '-')}",
        f"- **Audience:** {info.get('audience', '-')}",
        f"- **Personality:** {', '.join(info.get('personality', [])) or '-'}",
        f"- **Fonts:** {info['fonts']['display']} (display) / {info['fonts']['body']} (body) / {info['fonts']['mono']} (mono)",
        f"- **Shape / density / motion:** {spec.get('corner')} / {spec.get('density')} / {spec.get('motion')}",
        f"- **Contrast target:** WCAG 2.2 {spec.get('contrast', 'AA')} — smallest text pair "
        f"{stats['light']['minText']:.2f}:1 (light), {stats['dark']['minText']:.2f}:1 (dark)",
    ]
    if info.get("base"):
        lines.append(f"- **Derived from:** `{info['base']}`")
    lines += ["", "Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.", "",
              "## Key colors", "", "| Role | Light | Dark |", "| --- | --- | --- |"]
    for role in ("primary", "onPrimary", "primaryContainer", "secondary", "tertiary", "surface", "onSurface",
                 "outline", "error", "success", "warning", "info"):
        lines.append(f"| `{role}` | `{color('light', role)}` | `{color('dark', role)}` |")
    lines += ["", "## Design rationale", ""]
    for key, title in (("color", "Color"), ("typography", "Typography"), ("shape", "Shape and density"), ("motion", "Motion")):
        if rationale.get(key):
            lines += [f"**{title}.** {rationale[key]}", ""]
    if info.get("do"):
        lines += ["## Do", ""] + [f"- {item}" for item in info["do"]] + [""]
    if info.get("dont"):
        lines += ["## Don't", ""] + [f"- {item}" for item in info["dont"]] + [""]
    lines += ["## Source of truth", "",
              "`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.", ""]
    return "\n".join(lines)


def main() -> int:
    failed = False
    for entry in BUILTINS:
        tokens = ds_engine.build_tokens(entry["meta"], entry["spec"])
        errors, warnings = ds_validate.validate(tokens)
        target = L.BUILTIN_DIR / entry["meta"]["id"]
        L.write_json(target / "tokens.json", tokens)
        (target / "README.md").write_text(readme(tokens), encoding="utf-8")
        status = "FAIL" if errors else "ok"
        print(f"{entry['meta']['letter']} {entry['meta']['id']:<8} {status}  errors={len(errors)} warnings={len(warnings)}")
        for message in errors:
            print("   E " + message)
        for message in warnings:
            print("   W " + message)
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
