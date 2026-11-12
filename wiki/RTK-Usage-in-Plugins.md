# RTK — Usage in Plugins

This page documents how the [`ufil`](https://github.com/ghozimahdi/gm-claude-plugins/tree/main/plugins/ufil) plugin auto-installs and exposes RTK to end users. Other plugins in this repo don't currently bundle RTK — RTK is a **global** hook, so once UFIL activates it on one project, it benefits every Claude Code project on the same machine.

## Auto-install on session start

UFIL's `hooks/hooks.json` adds RTK's installer to the `SessionStart` event:

```jsonc
"SessionStart": [{
  "matcher": "",
  "hooks": [
    { "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/install-rtk.sh"
    }
  ]
}]
```

The `install-rtk.sh` script (in `plugins/ufil/scripts/`) is idempotent and always exits 0 — a failure never breaks the session:

1. **Install binary** if `rtk` isn't on `PATH`:
   - macOS + Homebrew → `brew install rtk`.
   - Otherwise → `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh`.
   - Both failed → log a hint, exit cleanly.
2. **Run `rtk init -g`** once to register the global Claude Code hook.
3. **Drop a sentinel file** at `${XDG_CACHE_HOME:-$HOME/.cache}/ufil/rtk-initialized` so subsequent `SessionStart` events skip the init step.

After step 2 succeeds the user is reminded to **restart Claude Code** so the new hook is picked up. Subsequent sessions get the rewrite automatically — no further action needed.

## User-facing commands

UFIL exposes three slash commands so users can manage RTK without leaving Claude Code:

| Command            | Purpose                                                                                       |
| ------------------ | --------------------------------------------------------------------------------------------- |
| `/rtk-status`      | Binary version + `rtk init --show` output + sentinel state. Calls out drift.                  |
| `/rtk-activate`    | Run `rtk init -g`, refresh the sentinel. Reminds user to restart Claude Code.                 |
| `/rtk-deactivate`  | Run `rtk init --uninstall`, remove the sentinel. RTK stays installed but the hook is removed. |

These commands are thin wrappers around the underlying `rtk` CLI — they don't add logic beyond surfacing the result and managing the UFIL sentinel.

## Why the sentinel?

The sentinel decouples **plugin state** from **RTK state**:

- `rtk init --show` is the authoritative source of truth for "is the hook active?" — UFIL never overrides this.
- The sentinel only answers "has *this plugin* already run `rtk init -g` at least once?" — used to skip the no-op `init` call on every session.

If they drift (sentinel says yes but `rtk init --show` says no, or vice versa), `/rtk-status` flags the drift so the user can run `/rtk-activate` or `/rtk-deactivate` to resync.

## Adopting RTK in a new plugin

If you write a new plugin that wants RTK, you have two reasonable options:

1. **Don't bundle it.** RTK is global. If the user already has UFIL installed, they already have RTK. Document RTK as a recommended companion, not a hard dependency.
2. **Mirror UFIL's pattern.** Copy `install-rtk.sh` (or write an equivalent), use your own sentinel path (e.g. `${XDG_CACHE_HOME:-$HOME/.cache}/<your-plugin>/rtk-initialized`), and add the script to your `SessionStart` hook. Provide `/rtk-status`-equivalents only if you want plugin-specific UX — otherwise let users use UFIL's.

Pitfalls to avoid:
- **Don't** `rtk init -g` on every session — it's a no-op but adds latency. Always sentinel-gate it.
- **Don't** assume the binary is `rtk-ai/rtk`. Have the script verify `rtk gain` is a recognized subcommand before trusting the binary on `PATH` (the install script in UFIL doesn't currently do this — see [RTK-Troubleshooting](RTK-Troubleshooting) for the manual check users should run).
- **Don't** swallow errors silently. Use stderr (`echo ... >&2`) like UFIL does so failures are visible in Claude Code's hook log, even though the script exits 0.
