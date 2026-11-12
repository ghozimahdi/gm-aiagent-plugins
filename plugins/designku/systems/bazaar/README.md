# Bazaar (C)

> High-energy and conversion-focused without shouting.

- **ID:** `bazaar`
- **Context:** E-commerce, marketplace, retail, deals
- **Audience:** Deal-seeking shoppers browsing fast with one thumb, comparing many items, often on mid-range Android devices.
- **Personality:** energetic, direct, generous, dependable
- **Fonts:** Plus Jakarta Sans (display) / Plus Jakarta Sans (body) / JetBrains Mono (mono)
- **Shape / density / motion:** soft / comfortable / snappy
- **Contrast target:** WCAG 2.2 AA — smallest text pair 4.59:1 (light), 5.01:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#C53700` | `#FFB5A0` |
| `onPrimary` | `#FFFFFF` | `#5F1500` |
| `primaryContainer` | `#FFDBD0` | `#862200` |
| `secondary` | `#904C29` | `#F7B99B` |
| `tertiary` | `#795900` | `#EDC060` |
| `surface` | `#FFF8F3` | `#18120E` |
| `onSurface` | `#201A16` | `#E9E1DB` |
| `outline` | `#867466` | `#A08D7F` |
| `error` | `#B4195D` | `#FFB1C6` |
| `success` | `#006E29` | `#8AD895` |
| `warning` | `#8A5100` | `#F8BA7D` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** A hot orange-red primary draws the eye to Buy and Add-to-cart; warm hues raise arousal and are the convention shoppers already know from major marketplaces. It is darkened to tone 45 so white button labels pass AA (most marketplace oranges do not). The secondary is a muted terracotta in the same hue family, so selected chips, tabs and tonal buttons read as part of the brand instead of introducing a second color; a bright yellow tertiary is the only accent, reserved for promos and ratings. Neutrals are a warm sand so greys never look cold next to the orange. Error is shifted to crimson so it can never be confused with the red-orange CTA, and it always carries an icon.

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
