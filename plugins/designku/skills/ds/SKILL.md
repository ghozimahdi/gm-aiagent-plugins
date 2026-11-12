---
name: ds
description: "designku workflow: list, use, apply, show, customize or create a design system from the catalog. Invoke with a sub-command, e.g. list, use aegis, apply, show, customize slate, create."
argument-hint: "<list|use <id>|apply|show|customize <id>|create>"
disable-model-invocation: true
---

Use the current user request as this skill's input. In Claude Code prefer the
dedicated commands (`/designku:ds-list`, `/designku:ds-use`, ...); this skill is
the shared entry point for Codex (`$designku:ds <sub-command>`), where plugin
commands are not available.

Resolve `DESIGNKU_ROOT` to the plugin root containing this skill (Claude Code:
`CLAUDE_PLUGIN_ROOT`; Codex: `PLUGIN_ROOT` or derive it from the installed
skill path). All workflows run one stdlib-only script:

```bash
python3 "${DESIGNKU_ROOT}/scripts/designku.py" <sub-command> [options]
```

| Request | Do |
| --- | --- |
| `list` | Run `list`. Show the table and every `file://` link verbatim. Then ask what to do: set as project default, customize an existing one, create new, or just browse. To pick among many systems, ask for the group first (the script prints `Pick groups`), then the system. |
| `use <id>` | Run `use <id>` from the Flutter project root, then do each printed `ACTION:` line (add `google_fonts`, wire `DsTheme.light` / `DsTheme.dark` into `MaterialApp`) and run `dart analyze` on the output folder. |
| `apply` | Run `apply` (after editing `.designku/tokens.json`). `--sync` re-copies tokens from the source system and discards local token edits — confirm first. |
| `show` | Run `show` and relay it. |
| `customize <id>` | Follow `${DESIGNKU_ROOT}/commands/ds-customize.md`: interview (brand color, mood, fonts, corners, density), then `derive --base <id> --name ...`. |
| `create` | Follow `${DESIGNKU_ROOT}/commands/ds-create.md`: UX interview (industry, audience, personality, accessibility), then `derive --name ... --primary ...`. |

Where a command file says to use AskUserQuestion and that tool is not
available, ask the same question in chat as a short numbered list and wait
for the answer. Never guess a brand color or skip the interview.

Custom systems are saved at user level (`~/.designku/systems/<id>/`) and appear
in `list` in every project. The per-project choice lives in
`.designku/config.json`.
