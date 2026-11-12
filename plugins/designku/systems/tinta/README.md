# Tinta (I)

> Neo-brutalism: ink outlines and hard offset shadows on warm paper, bold but still accessible.

- **ID:** `tinta`
- **Context:** Creator tools, content and video editing, indie SaaS, startups
- **Audience:** Creators, marketers and small teams who want a tool that feels confident and hand-made rather than corporate, and who return to it daily to make things.
- **Personality:** bold, honest, playful, crafted
- **Fonts:** Jost (display) / Mulish (body) / JetBrains Mono (mono)
- **Shape / density / motion:** soft / comfortable / snappy
- **Contrast target:** WCAG 2.2 AA — smallest text pair 4.68:1 (light), 4.97:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#1460ED` | `#A8C8FF` |
| `onPrimary` | `#FFFFFF` | `#00297A` |
| `primaryContainer` | `#E8F1FF` | `#263249` |
| `secondary` | `#465E8B` | `#B0C8F0` |
| `tertiary` | `#426900` | `#AAD382` |
| `surface` | `#F8F9F3` | `#141416` |
| `onSurface` | `#192C42` | `#EDEDF0` |
| `outline` | `#767967` | `#8E8E96` |
| `error` | `#AB3428` | `#FFB4A8` |
| `success` | `#3F6832` | `#ACD1A1` |
| `warning` | `#904D00` | `#FAB986` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Ported from the Cuplikin app. A saturated electric blue primary on an off-white, faintly green 'paper' background, with deep navy 'ink' for text, outlines and shadows instead of pure black, which keeps the brutalist contrast but softens it. Pastel mint, sky, peach and lavender containers act like highlighter marks for tags, credits and status, and the blue stays the only saturated color on screen. Dark mode switches to calm zinc greys and drops the hard shadow, because a light offset shadow on a dark surface looks like a rendering glitch.

**Typography.** Jost headlines (geometric, Futura-like, with a poster feel) pair with Mulish body text, which stays highly legible at small sizes in dense editor UIs.

**Shape and density.** Neo-brutalism: primary buttons, the FAB, elevated cards and dialogs get a 1.5px ink outline and a 3px hard shadow with zero blur. Pressing a button moves it into its shadow, so it feels physically pushed. Medium radii (12-16px) keep it friendly rather than raw. Secondary buttons, cards and inputs use thin light borders and no shadow, so the raised treatment always marks the one thing to press.

**Motion.** Snappy. The press-into-shadow translate is the main motion; everything else stays short.

## Do

- Give the hard shadow only to the single primary action per region (DsButton filled/danger, FAB) and to elevated cards or dialogs; everything else stays flat with thin borders.
- Use the pastel containers (primaryContainer = sky, tertiaryContainer = mint, warningContainer = peach) for badges, tags and credit or status chips.
- Keep text and outlines in onSurface (ink); never use pure black.

## Don't

- Do not hand-draw BoxShadow or borders in feature code. DsEffect and the Ds* atoms already apply the outline and hard shadow, and switch them off in dark mode.
- Do not stack several raised (shadowed) elements next to each other; neo-brutalism loses hierarchy when everything pops.
- Do not add blur to the shadow or color it with the brand blue; it is always a zero-blur ink offset.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
