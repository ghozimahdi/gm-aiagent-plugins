---
description: "Regenerate the Flutter design system code from this project's .designku/tokens.json (run after editing tokens)."
argument-hint: "[--sync] [--no-format]"
allowed-tools: ["Bash", "Read", "Edit"]
---

Generate platform code from the project's selected design system.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" apply $ARGUMENTS
```

- Source of truth is `.designku/tokens.json` in the project. To add or change a
  token (a new semantic color, a spacing step, a component size), edit that
  file, then run this command. Never edit the generated `.dart` files.
- `--sync` first re-copies the tokens from the source system (built-in or
  `~/.designku/systems/<id>`), **discarding project-local token edits** —
  confirm with the user before using it.
- The script validates the tokens (WCAG 2.2 contrast + structure) and refuses
  to generate if they fail. Report the failures and fix the tokens, not the
  validator.
- If there is no `.designku/config.json`, tell the user to run
  `/designku:ds-list` (or `/designku:ds-use <id>`) first.

Afterwards do each `ACTION:` line the script printed, run `dart analyze` on the
output folder, and summarize what changed.
