---
description: "Derive a new custom design system from an existing one: interview for brand color, mood, fonts, corners and density, regenerate accessible palettes, save to ~/.designku/systems and preview."
argument-hint: "<base-id|letter>"
allowed-tools: ["Bash", "AskUserQuestion", "Read"]
---

Act as a senior UI/UX designer. Derive a custom system from a base system.
Reply in the user's language. Never invent a brand color — always ask.

## 1. Resolve the base

Base = `$ARGUMENTS`. If empty, run
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" list` and ask which system
to start from (same two-step pick as `/designku:ds-list`). Read
`${CLAUDE_PLUGIN_ROOT}/systems/<id>/README.md` (or
`~/.designku/systems/<id>/README.md`) so you know what you are changing.

## 2. Interview (AskUserQuestion, max 4 options each — "Other" is always available)

Ask in at most two rounds; skip anything the user already stated.

Round 1:
- **Name** — plain question in chat if not given (it becomes the id, e.g. "Acme Brand" → `acme-brand`).
- **Brand color** (header `Brand color`): options `Keep base palette`, `I have a hex code` (they type it via Other / next message), plus two suggestions that fit their product and are clearly different hues. Accept any `#RRGGBB`.
- **Mood** (header `Mood`): `Calm`, `Balanced`, `Vibrant`, `Professional` — mention `warm` and `playful` are available via Other.

Round 2:
- **Font feel** (header `Fonts`): `Keep base fonts`, `Modern (Inter)`, `Friendly (Plus Jakarta Sans)`, `Elegant (Fraunces + DM Sans)` — other presets via Other: `geometric`, `soft`, `playful`, `editorial`, `technical`, `bold`, `accessible`, `readable`; or two family names from `designku.py fonts`.
- **Corner style** (header `Corners`): `Sharp`, `Soft`, `Rounded`, `Pill`.
- **Density** (header `Density`): `Compact`, `Comfortable`, `Spacious`.

Only ask about `--contrast AAA`, `--dark-style oled`, `--secondary` /
`--tertiary` hex if the user brings up accessibility needs, OLED/media, or
extra brand colors.

## 3. Generate

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" derive \
  --base <base-id> --name "<Name>" \
  [--primary "#RRGGBB"] [--secondary "#RRGGBB"] [--tertiary "#RRGGBB"] \
  [--mood calm|balanced|vibrant|professional|warm|playful] \
  [--font-style <preset> | --font-display "<Family>" --font-body "<Family>"] \
  [--corner sharp|soft|rounded|pill] [--density compact|comfortable|spacious] \
  [--motion snappy|balanced|expressive] [--contrast AA|AAA] [--dark-style tinted|oled] \
  [--context "<industry>"] [--audience "<who>"] [--personality "adj, adj, adj"] [--tagline "<one line>"]
```

Only pass the flags the user actually changed. The script regenerates the
tonal palettes from the seed color (CIE L* tone steps), validates every
text/background pair against WCAG 2.2 in light and dark, and saves to
`~/.designku/systems/<id>/` (`tokens.json`, `README.md`, `preview.html`) — a
user-level location, so the system shows up in `/designku:ds-list` in every
project.

If validation fails, nothing is saved: explain the failing pair in plain
language, propose a concrete fix (a slightly different seed, another mood), and
re-run. Never bypass the validator. Use `--force` only to overwrite a custom
system the user explicitly wants replaced.

## 4. Hand over

Show the `preview:` link on its own line, summarize the decisions as a
designer would (what changed vs. the base and why it suits their audience),
relay any `note:`/`warning:` lines, then ask (AskUserQuestion, header `Next`):
`Use in this project` (→ `/designku:ds-use <id>`), `Tweak again`, `Done`.
