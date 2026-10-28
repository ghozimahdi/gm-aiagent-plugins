# GM Claude Plugins — Wiki

Welcome. This wiki is the home for **cross-cutting documentation** that doesn't belong to any single plugin — tools, integrations, and conventions used by `ufil`, `rubyku`, and future plugins in this repository.

Plugin-specific docs (commands, agents, skills, hooks) stay inside each plugin folder. Anything shared — RTK, Dart MCP, hook conventions, marketplace mechanics — lives here.

## Topics

### ⚡ RTK (Rust Token Killer)

Token-saving CLI proxy that intercepts `git`, `flutter`, `dart`, `melos`, etc. and trims their output before it reaches Claude — 60–90% token reduction on common dev commands. UFIL auto-installs it on first session.

- [RTK — Overview](RTK)
- [Installation](RTK-Installation)
- [Commands](RTK-Commands)
- [Usage in Plugins](RTK-Usage-in-Plugins)
- [Troubleshooting](RTK-Troubleshooting)

### 🎯 Dart MCP — *coming soon*

Dart-native MCP server bundled with UFIL. Handles pub, build_runner, melos, and Flutter-specific analysis.

### 🪝 Hook conventions — *coming soon*

How the plugins compose Claude Code hooks (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) and the helper scripts they call.

## How this wiki works

This wiki is **mirrored from the [`wiki/`](https://github.com/ghozimahdi/gm-claude-plugins/tree/main/wiki) folder** in the main repo. Edits land via a regular pull request to `main`; a GitHub Action ([`sync-wiki.yml`](https://github.com/ghozimahdi/gm-claude-plugins/blob/main/.github/workflows/sync-wiki.yml)) pushes the changes to the Wiki repo on merge. Do not edit pages directly in the Wiki UI — they'll be overwritten on the next sync.

## License

MIT. See the repo `LICENSE` file.
