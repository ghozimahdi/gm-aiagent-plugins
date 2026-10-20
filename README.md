# GM Development Plugins

[![HOL Guard](https://img.shields.io/endpoint?url=https%3A%2F%2Fhol.org%2Fapi%2Fregistry%2Fbadges%2Fplugin%3Fslug%3Dghozimahdi%252Fgm-aiagent-plugins%26metric%3Dtrust)](https://hol.org/registry/plugins/ghozimahdi%2Fgm-aiagent-plugins)
[![Plugin Security Scan](https://github.com/ghozimahdi/gm-aiagent-plugins/actions/workflows/plugin-scanner.yml/badge.svg)](https://github.com/ghozimahdi/gm-aiagent-plugins/actions/workflows/plugin-scanner.yml)

A growing collection of Claude Code and Codex plugins for mobile, web & backend development by [Ghozi Mahdi](mailto:ghozi.dev@gmail.com).

**Focus:** Helping developers write code the right way — enforcing **best practices**, **clean architecture**, **standardized patterns**, and **industry conventions** so every project starts and stays on the right track.

Each plugin comes with opinionated rules, automated tooling, and AI-powered agents that guide you to follow proper standards — not just generate code, but generate _correct_ code.

## Available Plugins

| Plugin                        | Platform     | Description                                                                                                     |
| ----------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------- |
| [**ufil**](plugins/ufil/)     | Flutter/Dart | UFIL (Ultimate Flutter Intelligent Layer) — Clean Architecture + Modularization with Dart MCP & LSP integration |
| [**rubyku**](plugins/rubyku/) | Ruby/Rails   | Rails 8 development — Rails Way architecture, Hotwire-first frontend, Serena LSP for Ruby code intelligence     |
| _Coming soon_                 | React Native | TBD                                                                                                             |
| _Coming soon_                 | Kotlin       | TBD                                                                                                             |
| _Coming soon_                 | Express      | TBD                                                                                                             |

## What Makes These Plugins Different

- **Standards-first** — Every plugin enforces architecture patterns, naming conventions, and coding rules specific to its platform
- **Best practices built-in** — Not just scaffolding, but continuous enforcement through skills, agents, and hooks
- **AI-powered review** — Agents that review your code for architecture violations before you ship
- **Automated quality gates** — Pre-commit hooks, static analysis, and formatting baked in
- **Production-ready patterns** — Based on real-world project experience, not textbook examples

## Installation

### Claude Code

```bash
# 1. Add marketplace (one time)
/plugin marketplace add ghozimahdi/gm-aiagent-plugins

# 2. Install any plugin
/plugin install ufil@gm-aiagent-plugins
```

### Codex

```bash
# 1. Add marketplace (one time)
codex plugin marketplace add ghozimahdi/gm-aiagent-plugins

# 2. Install any plugin
codex plugin add ufil@gm-aiagent-plugins
```

After installation, invoke UFIL skills as `/ufil:<skill>` in Claude Code or
`$ufil:<skill>` in Codex.

Repository maintainers can run the shared release workflow with
`/release <plugin> [version]` in Claude Code or
`$release <plugin> [version]` in Codex.

## Documentation

Plugin-specific docs live next to each plugin. Cross-cutting topics — tools and integrations shared across plugins (Serena MCP, RTK, Dart MCP, hook conventions, etc.) — are documented in the [GitHub Wiki](https://github.com/ghozimahdi/gm-aiagent-plugins/wiki), which is mirrored from the [`wiki/`](wiki/) folder in this repo via [`.github/workflows/sync-wiki.yml`](.github/workflows/sync-wiki.yml) — edit pages there via a regular PR and they'll be pushed to the Wiki on merge to `main`.

If automated sync ever fails, you can push manually:

```bash
git clone git@github.com:ghozimahdi/gm-aiagent-plugins.wiki.git /tmp/gm-wiki
rsync -a --delete --exclude='.git' wiki/ /tmp/gm-wiki/
cd /tmp/gm-wiki && git add -A && git commit -m "Manual wiki sync" && git push
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE)
