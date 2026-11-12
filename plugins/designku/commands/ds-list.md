---
description: "Browse the design system catalog (built-in + your custom systems) with clickable HTML previews, then pick what to do: set as project default, customize, create new, or just browse."
argument-hint: "[--force]"
allowed-tools: ["Bash", "AskUserQuestion", "Read"]
---

List every design system and help the user choose. Reply in the user's language.

## Step 1 — Run the catalog script

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" list $ARGUMENTS
```

The script merges built-in systems with the user's custom systems
(`~/.designku/systems/`), re-renders stale `preview.html` files, rewrites
`~/.designku/catalog.html` and prints a table.

## Step 2 — Show the result

Relay the table to the user **verbatim in a code block**, keeping every
`file://` link on its own line so it stays clickable in the terminal. Point out:

- the **catalog** link (arrow keys move the selection, Enter opens a preview),
- the row marked `*` (current project default), if any.

Do not describe colors from memory and do not open a browser yourself.

## Step 3 — Ask what to do (AskUserQuestion)

Ask one question, header `Action`, with exactly these four options:

1. **Set as project default** — pick a system and generate the code
2. **Customize an existing one** — derive a new system from a base (brand color, fonts, corners)
3. **Create new** — design a system from scratch with a short UX interview
4. **Just browse** — stop here

## Step 4 — Pick a system (only for options 1 and 2)

AskUserQuestion allows at most 4 options, and the catalog has more systems
than that, so pick in two steps using the `Pick groups` block the script printed:

1. If there are 4 systems or fewer in total, list them directly and skip to 3.
2. Ask **which group** (header `Category`): one option per printed group
   (`Trust & Work`, `Commerce & Lifestyle`, `Care & Learning`, and
   `My custom systems` when the user has any). Use the group's system names as
   the option description.
3. Ask **which system** (header `System`) inside that group: one option per
   system, label = name, description = its context. If a group has more than
   4 systems (only possible for custom systems), show the 3 most recent — the
   script lists newest first — and tell the user they can type any other id
   via "Other".

The user can always answer "Other" with a system id or letter (A–H); accept it.

## Step 5 — Act

- **Set as project default** → follow `/designku:ds-use <id>`:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" use <id>` and then do
  that command's follow-up steps.
- **Customize** → follow `/designku:ds-customize <id>`.
- **Create new** → follow `/designku:ds-create`.
- **Just browse** → end with one line reminding them of
  `/designku:ds-use <id>`.
