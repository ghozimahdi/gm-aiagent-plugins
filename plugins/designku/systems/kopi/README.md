# Kopi (F)

> Warm, tactile and appetizing — a menu, not a dashboard.

- **ID:** `kopi`
- **Context:** Food and beverage, cafes, restaurants, travel, lifestyle, hospitality
- **Audience:** Customers ordering or browsing at leisure; emotional, sensory decisions driven by photography.
- **Personality:** warm, crafted, inviting, unpretentious
- **Fonts:** Fraunces (display) / DM Sans (body) / JetBrains Mono (mono)
- **Shape / density / motion:** soft / comfortable / balanced
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.54:1 (light), 4.99:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#835332` | `#EABEA1` |
| `onPrimary` | `#FFFFFF` | `#502500` |
| `primaryContainer` | `#F7DECD` | `#693B1A` |
| `secondary` | `#775840` | `#DEC1AC` |
| `tertiary` | `#885200` | `#F8BB7B` |
| `surface` | `#FFF8F0` | `#17130C` |
| `onSurface` | `#201B14` | `#E8E1D9` |
| `outline` | `#847561` | `#9E8E7A` |
| `error` | `#B81A42` | `#FFB2B8` |
| `success` | `#006E29` | `#8AD895` |
| `warning` | `#8A5100` | `#F8BA7D` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Roasted-coffee brown is earthy and appetizing and, unlike saturated red or orange, never fights with food photography. A muted latte secondary keeps selected and tonal states inside the coffee family; caramel-saffron tertiary highlights specials. Neutrals are a warm cream (higher chroma, hue 75) instead of clinical white, like paper or linen.

**Typography.** Fraunces, a soft old-style serif, gives headlines the feel of a printed menu. DM Sans body keeps prices and options clean and modern.

**Shape and density.** Soft 8-16px corners, comfortable density. Cards are image-first with generous padding.

**Motion.** Balanced and gentle; image fades and sheet transitions use the slow duration.

## Do

- Let photography carry the color; keep chrome on cream surfaces.
- Use headline styles (serif) for dish and place names, body (sans) for descriptions and prices.
- Use tertiaryContainer for 'new' and 'chef's pick' labels.

## Don't

- Do not set long paragraphs in the serif display family — it is for headlines only.
- Do not place text directly on photos without a scrim.
- Do not use pure white cards; surfaceContainerLowest is the brightest surface and should be used sparingly.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
