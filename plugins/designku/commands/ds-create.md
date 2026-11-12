---
description: "Create a new design system from scratch with a short UX-research interview (audience, industry, personality, accessibility), save it to ~/.designku/systems and preview it."
argument-hint: "[name]"
allowed-tools: ["Bash", "AskUserQuestion", "Read"]
---

Act as a senior UI/UX designer and UX researcher. Design a new system from
scratch. Reply in the user's language. Do not assume: every decision below
comes from an answer or from stated reasoning the user can veto.

## 1. Research interview (AskUserQuestion; "Other" is always available)

Round 1 — who and what:
- **Name** — `$ARGUMENTS` or ask in chat.
- **Industry** (header `Industry`): `Finance / business`, `Commerce / lifestyle`, `Health / education`, `Social / entertainment`.
- **Audience** (header `Audience`): `General adults`, `Young (Gen Z)`, `Kids / family`, `Seniors / low vision`.
- **Personality** (header `Personality`, multiSelect): `Trustworthy`, `Playful`, `Premium`, `Energetic` — more adjectives via Other.

Round 2 — look:
- **Brand color** (header `Brand color`): `I have a hex code`, plus three
  suggestions you derive from round 1. Give each a one-line reason
  (e.g. "Deep teal #0F766E — calm + trustworthy, distinct from the usual
  fintech blue"). Suggestions must be different hues.
- **Corners** (header `Corners`): `Sharp`, `Soft`, `Rounded`, `Pill`.
- **Density** (header `Density`): `Compact`, `Comfortable`, `Spacious`.
- **Accessibility** (header `Contrast`): `Standard (WCAG AA)`, `Enhanced (WCAG AAA)`.

## 2. Translate answers into a spec (state your reasoning in 3–5 lines first)

| Signal | Decision |
| --- | --- |
| Finance, enterprise, "trustworthy" | `--mood professional`, `--font-style geometric` or `technical`, `--corner soft`, `--motion balanced` |
| Commerce, "energetic" | `--mood vibrant`, `--font-style friendly`, `--motion snappy` |
| Health, "calm" | `--mood calm`, `--font-style soft`, `--corner pill`, `--density spacious` |
| Kids / family, "playful" | `--mood playful`, `--font-style playful`, `--corner rounded`, `--density spacious`, `--motion expressive` |
| Food, travel, "warm", "premium" | `--mood warm`, `--font-style elegant` |
| Social, Gen Z | `--mood vibrant`, `--font-style bold`, `--corner pill`, `--dark-style oled`, `--motion expressive` |
| Seniors / low vision | `--contrast AAA`, `--font-style accessible` or `readable`, `--density spacious` |
| Dense data, power users | `--density compact`, `--corner sharp`, `--motion snappy` |

When a built-in is already close, say so and offer
`/designku:ds-customize <id>` instead.

## 3. Generate

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" derive \
  --name "<Name>" --primary "#RRGGBB" --mood <mood> \
  --font-style <preset> --corner <corner> --density <density> --motion <motion> \
  --contrast <AA|AAA> [--dark-style oled] [--secondary "#RRGGBB"] [--tertiary "#RRGGBB"] \
  --context "<industry / product>" --audience "<who, in one sentence>" \
  --personality "<adj, adj, adj>" --tagline "<one line>"
```

`--primary` is required when there is no `--base`. Secondary and tertiary
colors are derived from the primary and the mood unless given. The script
validates WCAG 2.2 contrast for every pair in light and dark and saves to
`~/.designku/systems/<id>/` (user level — reusable in every project). On
failure nothing is saved; explain and adjust, never bypass.

## 4. Hand over

Show the `preview:` link on its own line, a short designer's rationale
(audience → palette, type, shape, motion), any `note:`/`warning:` lines, then
ask (AskUserQuestion, header `Next`): `Use in this project`
(→ `/designku:ds-use <id>`), `Tweak it` (→ `/designku:ds-customize <id>`),
`Done`.
