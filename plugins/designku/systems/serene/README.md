# Serene (B)

> Low-arousal and reassuring, for people who may already be stressed.

- **ID:** `serene`
- **Context:** Health, wellness, telemedicine, mental health, habit tracking
- **Audience:** Patients and self-carers of all ages, including older adults and people using the app while unwell, tired or worried.
- **Personality:** calm, caring, clear, unhurried
- **Fonts:** Outfit (display) / Figtree (body) / JetBrains Mono (mono)
- **Shape / density / motion:** pill / spacious / balanced
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.56:1 (light), 5.00:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#166A5C` | `#88D5C3` |
| `onPrimary` | `#FFFFFF` | `#00382F` |
| `primaryContainer` | `#A4F1DF` | `#005144` |
| `secondary` | `#45636C` | `#ACCCD7` |
| `tertiary` | `#934A2D` | `#FFB59A` |
| `surface` | `#F2FBF9` | `#0E1513` |
| `onSurface` | `#161D1B` | `#DCE4E2` |
| `outline` | `#667B76` | `#809590` |
| `error` | `#BA1A1A` | `#FFB4AA` |
| `success` | `#006E29` | `#76DC87` |
| `warning` | `#8A5100` | `#FFB870` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** A muted sage-teal sits between blue (clinical trust) and green (health, growth) and has low arousal, which lowers perceived urgency. The warm clay tertiary adds human warmth so the product does not feel like a hospital. Saturation is deliberately capped; the only loud color on screen should be a genuine alert.

**Typography.** Outfit headlines are soft and geometric; Figtree body text has open apertures and generous spacing that hold up for older eyes and at larger dynamic type sizes.

**Shape and density.** Pill buttons and large radii read as gentle and safe. Spacious layout reduces cognitive load when the user is not at their best.

**Motion.** Balanced timing with standard easing — slow enough to feel calm, never animated for decoration.

## Do

- Lead with one clear next step per screen; keep secondary actions as text buttons.
- Use the container tones (primaryContainer, tertiaryContainer) for large calm areas instead of solid primary.
- Reserve error for clinically important alerts and always explain what to do next.

## Don't

- Do not use red for routine things such as an incomplete habit or a missed streak — it induces guilt.
- Do not shrink body text below bodyMedium; many users will have their system font size raised.
- Do not use countdown timers, badges or urgency patterns.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
