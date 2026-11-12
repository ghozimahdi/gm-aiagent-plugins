# Bazaar (C)

> High-energy and conversion-focused without shouting.

- **ID:** `bazaar`
- **Context:** E-commerce, marketplace, retail, deals
- **Audience:** Deal-seeking shoppers browsing fast with one thumb, comparing many items, often on mid-range Android devices.
- **Personality:** energetic, direct, generous, dependable
- **Fonts:** Plus Jakarta Sans (display) / Plus Jakarta Sans (body) / JetBrains Mono (mono)
- **Shape / density / motion:** soft / comfortable / snappy
- **Contrast target:** WCAG 2.2 AA — smallest text pair 4.61:1 (light), 5.02:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#BA4400` | `#FFB599` |
| `onPrimary` | `#FFFFFF` | `#591C00` |
| `primaryContainer` | `#FFDBCD` | `#7E2C00` |
| `secondary` | `#425E92` | `#A8C8FF` |
| `tertiary` | `#795900` | `#F7BE34` |
| `surface` | `#FDF9F5` | `#151311` |
| `onSurface` | `#1E1B19` | `#E6E2DF` |
| `outline` | `#7F756D` | `#998F87` |
| `error` | `#B4195D` | `#FFB1C6` |
| `success` | `#006E29` | `#76DC87` |
| `warning` | `#8A5100` | `#FFB870` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** A hot orange-red primary draws the eye to Buy and Add-to-cart; warm hues raise arousal and are the convention shoppers already know from major marketplaces. It is darkened to tone 45 so white button labels pass AA (most marketplace oranges do not). A deep navy secondary anchors checkout and payment screens with trust, and a bright yellow tertiary is reserved for promos and ratings. Error is shifted to crimson so it can never be confused with the orange CTA.

**Typography.** Plus Jakarta Sans throughout: friendly, compact, and its bold weights keep prices punchy at small sizes.

**Shape and density.** Soft 8-12px corners maximize the image area on product cards. Comfortable density keeps the buy button a full 48px.

**Motion.** Snappy (80% durations) — browsing should feel fast; add-to-cart feedback is immediate.

## Do

- Keep exactly one filled primary button visible in the sticky bottom bar (Add to cart / Buy now).
- Show price in titleLarge with strong weight; strike-through prices use onSurfaceVariant.
- Use tertiaryContainer for promo chips and star ratings.

## Don't

- Do not use primary for discounts and errors at the same time — discount badges use tertiary, failures use error.
- Do not put primary-colored text on surfaceContainerHigh/Highest (contrast drops below AA for text).
- Do not animate every card; motion budget goes to cart and checkout feedback.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
