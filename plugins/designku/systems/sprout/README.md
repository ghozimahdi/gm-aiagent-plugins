# Sprout (E)

> Playful and encouraging, with big targets for small (or distracted) hands.

- **ID:** `sprout`
- **Context:** Education, kids and family, language learning, gamified habits
- **Audience:** Children 6-12 with a parent nearby, and casual adult learners doing five-minute sessions; developing readers and imprecise motor control.
- **Personality:** playful, encouraging, bright, safe
- **Fonts:** Baloo 2 (display) / Nunito (body) / JetBrains Mono (mono)
- **Shape / density / motion:** rounded / spacious / expressive
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.53:1 (light), 4.99:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#216D00` | `#94D783` |
| `onPrimary` | `#FFFFFF` | `#0D3900` |
| `primaryContainer` | `#C7EDBD` | `#175200` |
| `secondary` | `#3F6918` | `#ABD292` |
| `tertiary` | `#795900` | `#ECC163` |
| `surface` | `#F9FAF1` | `#13140E` |
| `onSurface` | `#1C1C16` | `#E2E3DA` |
| `outline` | `#777864` | `#91927D` |
| `error` | `#BA1A1A` | `#FFB4AA` |
| `success` | `#006E29` | `#8AD895` |
| `warning` | `#8A5100` | `#F8BA7D` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Leaf green signals growth and 'correct', and is gender-neutral for children. A softer leaf-green secondary keeps selection and tonal states in the brand family, and a sunshine yellow tertiary supplies the playful accent for stars, streaks and rewards. Because green doubles as success, wrong answers use an error container with an icon and a gentle message rather than a red screen.

**Typography.** Baloo 2 headlines are chunky and friendly. Nunito body has rounded terminals and clearly distinct letterforms (a, g, l, I), which helps early readers.

**Shape and density.** Rounded 16-24px corners and spacious density: 52px buttons and 72px list rows forgive imprecise taps.

**Motion.** Expressive: 120% durations and an overshoot curve on the emphasized easing make rewards feel alive. Always respect reduce-motion.

## Do

- Celebrate progress with tertiary (stars, streaks) and primary (correct, continue).
- Use icons plus words on every button; never rely on reading alone or color alone.
- Keep one task per screen with a large primary button anchored at the bottom.

## Don't

- Do not punish with red full-screen states; use errorContainer and an encouraging retry.
- Do not go below bodyLarge for instructions aimed at children.
- Do not place destructive or purchase actions near the primary button.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
