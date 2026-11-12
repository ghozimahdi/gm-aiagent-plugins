# Focus (D)

> Quiet chrome so the user's content is the interface.

- **ID:** `focus`
- **Context:** Productivity, tasks, notes, project tools, SaaS
- **Audience:** Knowledge workers in long sessions who return many times a day and value speed and keyboard-like efficiency.
- **Personality:** focused, efficient, modern, unobtrusive
- **Fonts:** Inter (display) / Inter (body) / JetBrains Mono (mono)
- **Shape / density / motion:** soft / compact / snappy
- **Contrast target:** WCAG 2.2 AA — smallest text pair 5.55:1 (light), 4.98:1 (dark)

Open [`preview.html`](preview.html) in a browser to see every token, atom, molecule, organism, template and page.

## Key colors

| Role | Light | Dark |
| --- | --- | --- |
| `primary` | `#4E44E3` | `#B9C3FF` |
| `onPrimary` | `#FFFFFF` | `#2B009E` |
| `primaryContainer` | `#DBE1FF` | `#3C23C6` |
| `secondary` | `#555F71` | `#BEC7D7` |
| `tertiary` | `#006A60` | `#87D5C8` |
| `surface` | `#F8F9FD` | `#131316` |
| `onSurface` | `#1B1B1E` | `#E1E2E6` |
| `outline` | `#757780` | `#8E909A` |
| `error` | `#BA1A1A` | `#FFB4AA` |
| `success` | `#006E29` | `#8AD895` |
| `warning` | `#8A5100` | `#F8BA7D` |
| `info` | `#005DB6` | `#A0CAFF` |

## Design rationale

**Color.** Indigo is distinctive yet recedes behind content, and reads as 'tool' rather than 'brand campaign'. Secondary is a true slate grey so most of the UI is near-monochrome; the teal tertiary is used sparingly for tags and progress. Low neutral chroma keeps long reading sessions free of color cast.

**Typography.** Inter everywhere: purpose-built for UI, excellent at 12-14px, with tabular numerals for dates and counts.

**Shape and density.** Soft 8-12px radii and compact density (40px buttons, 56px rows) fit more information per screen while each row keeps a 48px+ touch target.

**Motion.** Snappy. Frequent actions (check off, archive) must feel instant; nothing lasts beyond 240ms except full-screen transitions.

## Do

- Use surface containers and dividers to build hierarchy before reaching for color.
- Use primary for the current selection and the single create action (FAB or app-bar button).
- Keep list rows scannable: titleSmall + bodySmall, one trailing meta item.

## Don't

- Do not color-code more than five categories; add an icon or label to every tag color.
- Do not use display styles inside task lists — headlineSmall is the practical maximum.
- Do not add shadows to list items; elevation is for overlays only.

## Source of truth

`tokens.json` (W3C DTCG format). Never hand-edit generated platform code; change the tokens and run `/designku:ds-apply`.
