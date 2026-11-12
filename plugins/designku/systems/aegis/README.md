# Aegis (A)

> Calm authority for money and sensitive data.

- **ID:** `aegis`
- **Context:** Fintech, banking, insurance, payments
- **Audience:** Adults 22-55 moving their own money; anxious about mistakes, scanning numbers on the go, often outdoors in bright light.
- **Personality:** trustworthy, precise, composed, premium
- **Fonts:** Manrope (display) / Public Sans (body) / JetBrains Mono (mono)
- **Shape / density / motion:** rounded / comfortable / balanced
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.54:1 (light), 5.01:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#1F54D2` | `#AAC7FF` |
| `onPrimary` | `#FFFFFF` | `#00228A` |
| `primaryContainer` | `#D5E3FF` | `#0738B5` |
| `secondary` | `#4A607C` | `#B0C9E8` |
| `tertiary` | `#7D5700` | `#F1BE69` |
| `surface` | `#F7F9FF` | `#111317` |
| `onSurface` | `#1A1C1F` | `#E0E3E8` |
| `outline` | `#717784` | `#8A919E` |
| `error` | `#BA1A1A` | `#FFB4AA` |
| `success` | `#006E29` | `#76DC87` |
| `warning` | `#8A5100` | `#FFB870` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Deep cobalt blue is the most consistently trust-associated hue across markets and stays legible in sunlight. A desaturated blue-slate secondary keeps dense screens quiet, and a restrained gold tertiary marks rewards and premium tiers without competing with the primary call to action. Neutrals carry a faint blue tint so greys never look dirty next to the brand color.

**Typography.** Manrope headlines have open, unambiguous numerals (critical for balances and amounts). Public Sans body text is plain and institutional, which reads as honest rather than promotional.

**Shape and density.** Rounded 12-16px corners soften a serious palette just enough to feel modern, not bureaucratic. Comfortable density with 48px controls because a mis-tap on a transfer is expensive.

**Motion.** Balanced, never bouncy. Money movements should feel deliberate; confirmation states get the slow duration so users notice them.

## Do

- Use primary only for the single most important action per screen (Pay, Transfer, Confirm).
- Show amounts in titleLarge or larger; use the mono family for account numbers and tabular figures.
- Pair every success/error state with an icon and plain-language text ("Transfer sent"), not color alone.

## Don't

- Do not use the gold tertiary for buttons or errors — it is a reward/premium accent only.
- Do not color negative amounts with error red unless the value is an actual problem; use onSurface with a minus sign.
- Do not stack more than one filled button in a view.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
