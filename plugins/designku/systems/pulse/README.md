# Pulse (G)

> Vibrant and expressive, built dark-first for media.

- **ID:** `pulse`
- **Context:** Social, community, creator tools, entertainment, events, dating
- **Audience:** Gen Z and young millennials in short, frequent, often night-time sessions; content is user-generated photo and video.
- **Personality:** bold, expressive, youthful, immersive
- **Fonts:** Sora (display) / Be Vietnam Pro (body) / JetBrains Mono (mono)
- **Shape / density / motion:** pill / comfortable / expressive
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.55:1 (light), 4.99:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#B1008D` | `#FFADE3` |
| `onPrimary` | `#FFFFFF` | `#60004B` |
| `primaryContainer` | `#FFD7F0` | `#87006B` |
| `secondary` | `#6642CF` | `#C5C0FF` |
| `tertiary` | `#006780` | `#67D4F7` |
| `surface` | `#FFF7FC` | `#120D10` |
| `onSurface` | `#1F1A1D` | `#E8E0E5` |
| `outline` | `#83727D` | `#9D8C97` |
| `error` | `#BA1A00` | `#FFB4A5` |
| `success` | `#006E29` | `#76DC87` |
| `warning` | `#8A5100` | `#FFB870` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Electric magenta is high-arousal and ownable in a category crowded with blue. Violet secondary and cyan tertiary form a wide triad for stories, reactions and live states. Dark mode uses a near-black tinted surface (the one context where it is appropriate) so media pops and OLED screens save power — but never pure #000, which smears when scrolling.

**Typography.** Sora headlines are wide and confident; Be Vietnam Pro body text stays readable in dense comment threads.

**Shape and density.** Pill buttons and chips, large card radii — everything feels tappable and soft. Comfortable density.

**Motion.** Expressive: overshoot on likes and reactions; 120% durations. Always respect reduce-motion.

## Do

- Design dark-first and verify light mode second.
- Use primary for the main social action (Post, Follow) and for active nav state.
- Use gradients only between adjacent tonal steps of one palette if at all.

## Don't

- Do not place magenta text on photos or video without a scrim.
- Do not use primary and error side by side (hues are 40° apart) — destructive actions need an icon and a confirmation.
- Do not use all three accent colors on one component.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
