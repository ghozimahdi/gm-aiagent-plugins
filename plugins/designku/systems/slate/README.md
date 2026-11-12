# Slate (H)

> Neutral monochrome that disappears behind data — and behind any brand.

- **ID:** `slate`
- **Context:** Enterprise, B2B, admin, internal tools, white-label base
- **Audience:** Professionals using dense, data-heavy screens under time pressure; also teams who need a neutral base to re-skin per client.
- **Personality:** neutral, rigorous, dense, durable
- **Fonts:** IBM Plex Sans (display) / IBM Plex Sans (body) / IBM Plex Mono (mono)
- **Shape / density / motion:** sharp / compact / snappy
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.56:1 (light), 5.48:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#29313D` | `#DEE3EA` |
| `onPrimary` | `#FFFFFF` | `#29313D` |
| `primaryContainer` | `#DEE3EA` | `#3F4754` |
| `secondary` | `#555F6D` | `#BEC7D4` |
| `tertiary` | `#1557C9` | `#A7C8FF` |
| `surface` | `#F8F9FC` | `#121315` |
| `onSurface` | `#1A1C1D` | `#E1E3E5` |
| `outline` | `#72777F` | `#8C9199` |
| `error` | `#BA1A1A` | `#FFB4AA` |
| `success` | `#006E29` | `#8AD895` |
| `warning` | `#8A5100` | `#F8BA7D` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** A graphite near-black primary gives maximum contrast and zero brand bias, so status colors and charts carry all the meaning. A single blue tertiary is kept for links, focus and selection. This is also the safest starting point for /designku:ds-customize.

**Typography.** IBM Plex Sans has an engineered, technical voice with distinct glyphs for I, l and 1; IBM Plex Mono for IDs and codes.

**Shape and density.** Sharp 4-8px corners and compact density read as professional tooling and maximize data per screen.

**Motion.** Snappy and functional only.

## Do

- Use tertiary (blue) for links, focus rings and selected rows; primary (graphite) for the main button.
- Encode status with color + icon + label; this system is designed for many status chips.
- Use the mono family for identifiers, codes and aligned numeric columns.

## Don't

- Do not introduce new accent colors per feature; extend tokens.json if a category color is truly needed.
- Do not use elevation for static cards — use outlineVariant borders.
- Do not reduce row height below size.listItem to fit more data.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
