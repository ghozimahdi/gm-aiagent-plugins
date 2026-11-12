# UFIL (Ultimate Flutter Intelligent Layer)

A Claude Code and Codex plugin for Flutter Clean Architecture + Modularization with Dart MCP integration.

Supports both **modular** (multi-package + melos) and **single-module** project structures.

## What's Included

### Claude Code Agents (3)

| Agent            | Role                                                | Model  |
| ---------------- | --------------------------------------------------- | ------ |
| `gm-architect`   | Plans features, designs architecture, creates tasks | Opus   |
| `gm-implementer` | Writes production code following standards          | Sonnet |
| `gm-reviewer`    | Reviews code for architecture violations            | Sonnet |

### Shared Skills (24)

UFIL exposes the same skills to both clients:

- Claude Code: `/ufil:<skill> [arguments]`
- Codex: `$ufil:<skill> [arguments]`

Skills split into two kinds. The kind is visible directly in each `SKILL.md`'s
frontmatter, so a diff always tells you which one changed without needing git
archaeology:

| Kind                 | Frontmatter marker                                | Behavior                                                                                                                                                        |
| -------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Workflow skills**  | `disable-model-invocation: true` + `argument-hint` | Explicit action, invoked manually with arguments. Originated as `commands/*.md` files and were migrated into `skills/<name>/SKILL.md` (commits `8a9e1e7`, `6dc79d2`) so one file works as a slash command in both clients. |
| **Reference skills** | neither field set                                  | Auto-loaded by the model when relevant (architecture/pattern knowledge). Take no arguments; were never commands.                                              |

`argument-hint` is a Claude Code-only frontmatter extension (shown in the `/`
autocomplete menu) — Codex ignores it silently, so it's safe to set on shared
skill files.

Architecture and convention skills (reference — auto-invoked, no arguments):

| Skill                 | Description                                                       |
| --------------------- | ----------------------------------------------------------------- |
| `clean-architecture`  | Model, DTO, repository, usecase, datasource patterns              |
| `bloc-pattern`        | Events, states (sub-state unions), BlocProvider, ScreenUtil        |
| `testing-conventions` | bloc_test, mocktail, Result helpers, directory structure           |
| `melos`               | Workspace config, scripts, modular vs single-package usage         |
| `auto-route`          | Modular (RouteProvider) vs non-modular (single AppRouter) routing  |
| `injectable-di`       | Modular (per-package DI + Config) vs non-modular (single injector) |
| `freezed`             | Model, DTO, state, event, failure, params patterns                 |
| `flutter-performance` | Const class vs helper, isolate vs compute, ListView optimization   |

Workflow skills (action — migrated from `commands/*.md`, invoked explicitly):

| Skill               | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `init-project`      | Scaffold new project (modular or single-module)                   |
| `generate-module`   | Generate feature module (domain/data/presentation)                |
| `create-bloc`       | Create a BLoC (3 files: bloc/event/state)                         |
| `build`             | Run code generation (freezed, injectable, auto_route, etc.)       |
| `check`             | Static analysis + formatting before commit                        |
| `test`              | Run tests and report results                                      |
| `plan`              | Plan an issue and save it under the target project's `.ufil/`     |
| `implement`         | Implement a feature following clean architecture                  |
| `implement-batch`   | Implement multiple features in parallel                           |
| `commit`            | Git commit with Conventional Commits                              |
| `create-pr`         | Create GitHub PR with structured summary and test plan            |
| `ship`              | Tests + review + commit + PR                                      |
| `review`            | Audit codebase for architecture violations                        |
| `write-test`        | Write tests for a feature or file                                 |
| `keep-alive`        | Prevent macOS from auto-sleeping (toggle on/off/status)           |

### Claude-only RTK Commands

These live in `commands/*.md`, not `skills/` — the only files in the plugin
still using the legacy Command format. RTK manages Claude Code's global Bash
hook, a Claude-only concern, so they were intentionally left out of the
commands-to-skills migration and have no Codex equivalent:

- `/ufil:rtk-status`
- `/ufil:rtk-activate`
- `/ufil:rtk-deactivate`

### Hooks

- **Pre-commit**: Auto-runs `fvm dart fix --apply` + `fvm dart format` + `fvm dart analyze` before every git commit
- **Post-edit**: Reminds to analyze after editing .dart files
- **Claude SessionStart**: Auto-installs and initializes [rtk-ai/rtk](https://github.com/rtk-ai/rtk). The installer intentionally skips Codex because RTK configures Claude's global Bash hook.

### MCP Servers

- **Dart & Flutter MCP Server**: pub.dev search, error analysis, dependency management

### Claude Code LSP Server

- **Dart LSP**: Built-in diagnostics after every edit

### Other

- **.claudeignore**: Template for Flutter projects (skips generated code, build outputs, binary assets)

## Project Types

### Modular (multi-package + melos)

```
project/
├── app/                          # Main Flutter app
├── packages/
│   ├── library/library_common/   # Flavor, AppEnv, AppConfig
│   ├── domain/domain_common/     # Failure model, DataSourceConfig interface
│   ├── domain/domain_<feature>/  # Entities, repos, usecases
│   ├── data/data_common/         # Dio, interceptors, local storage
│   ├── data/data_<feature>/      # DTOs, datasources, repo impls
│   ├── presentation/feature_common/ # Theme, widgets, route providers
│   └── presentation/feature_<feature>/ # Pages, blocs, routes
└── pubspec.yaml                  # Melos workspace
```

### Single-module

```
project/
├── lib/
│   ├── core/                     # DI, router, error, network, theme
│   ├── features/<feature>/       # domain/ + data/ + presentation/
│   ├── common/                   # Shared across features
│   ├── injector.dart
│   ├── app_router.dart
│   └── main.dart
└── pubspec.yaml
```

## Installation

### Codex

```bash
# From GitHub
codex plugin marketplace add ghozimahdi/gm-aiagent-plugins
codex plugin add ufil@gm-aiagent-plugins

# Or from a local clone
codex plugin marketplace add /absolute/path/to/gm-aiagent-plugins
codex plugin add ufil@gm-aiagent-plugins
```

Start a new Codex conversation after installation so its skills, hooks, and MCP
tools are loaded. Invoke workflows with `$ufil:<skill>`, for example:

```text
$ufil:init-project my_app --package com.example.app --modular
$ufil:plan 123
$ufil:implement 123
```

Codex consumes the shared workflow skills directly. The three Claude agent
definitions are also usable as role guidance by orchestration skills, although
they are not registered as named Codex agents. Claude's Dart LSP configuration
and RTK global-hook commands remain Claude-only.

### Claude Code

```bash
# From GitHub
/plugin marketplace add ghozimahdi/gm-aiagent-plugins
/plugin install ufil@gm-aiagent-plugins

# Or local plugin directory
cd /path/to/your-flutter-project
claude --plugin-dir /path/to/gm-aiagent-plugins/plugins/ufil
```

Invoke workflows with the plugin-qualified skill name:

```text
/ufil:init-project my_app --package com.example.app --modular
/ufil:plan 123
/ufil:implement 123
```

## Standards Enforced

- Clean Architecture (Presentation -> Domain -> Data)
- Bloc only (never Cubit or raw setState)
- Freezed for all models, states, events
- `@injectable` for DI (never manual getIt.register\*)
- Dio for networking
- Separate `@lazySingleton` mapper classes (never `.toModel()` on DTO)
- ScreenUtil with semantic axes; empty gaps use `N.verticalSpace`/`N.horizontalSpace`
- Sub-state freezed unions per async action (never flat bool flags)

## Version Detection

This plugin **auto-detects all versions** at project creation time — zero hardcoded dependency versions:

| What | Source | Example |
|------|--------|---------|
| Dart SDK constraint | `fvm dart --version` | `^3.7.0` |
| Flutter version (.fvmrc) | `fvm flutter --version` | `3.41.6` |
| All packages (melos, dio, freezed, etc.) | `fvm dart pub add` (pub.dev) | Always latest |

## Requirements

- **FVM** (required) — `dart pub global activate fvm`, then `fvm install <version> && fvm global <version>`
- Dart SDK 3.6+ (for pub workspaces / melos 7.x)
- Flutter SDK managed through FVM
- **RTK** (optional, Claude Code only) — auto-installed on first Claude session

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before submitting a pull request. All changes must go through the **fork + PR** workflow.

For collaboration inquiries: **ghozi.dev@gmail.com**

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
