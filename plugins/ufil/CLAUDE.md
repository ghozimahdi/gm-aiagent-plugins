# UFIL (Ultimate Flutter Intelligent Layer)

This plugin provides GM's standardized Flutter development environment for Claude Code and Codex.
Supports both **modular** (multi-package + melos) and **single-module** project structures.

## What's Included

- **3 Agents**: Architect, Implementer, Reviewer
- **23 shared skills** (`skills/`, shared with Codex): 8 architecture/convention skills (reference — auto-invoked, no frontmatter markers) and 15 workflow skills (action — `disable-model-invocation: true` + `argument-hint` in frontmatter, migrated from `commands/*.md`; see README.md for the full split and migration commits)
- **3 Claude-only commands** (`commands/*.md`, legacy Command format, no Codex equivalent): rtk-activate, rtk-deactivate, rtk-status
- **Team Config**: `config/team-config.json` — thresholds + max parallel agents. `/ufil:implement` auto-detects ticket scope and switches to team mode (architect → parallel implementers in worktrees) when thresholds are exceeded. Tune without editing skill files.
- **Hooks**: Auto dart fix + format + analyze before git commit
- **MCP Servers**: Dart & Flutter MCP Server
- **Dart LSP**: Code intelligence (go-to-definition, find references, diagnostics)
- **RTK auto-install**: [rtk-ai/rtk](https://github.com/rtk-ai/rtk) CLI proxy installed and globally registered on first session — cuts Claude Code token usage 60-90% on `git`, `flutter`, `dart`, `melos`, etc.
- **.claudeignore**: Template for Flutter projects

## Project Types

| Type              | Structure                                              | DI                                 | Error Handling                                                                         | Mappers                                                           |
| ----------------- | ------------------------------------------------------ | ---------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Modular**       | `app/` + `packages/{library,domain,data,presentation}` | Per-package di.dart + Config class | Query: Result model (Failure + data) / Action: `Future<Failure>` + FailureHandlerMixin | Separate `@lazySingleton` mapper classes (NO `.toModel()` on DTO) |
| **Single-module** | `lib/{core,features,common}`                           | Single injector.dart               | `Result<T>` + ErrorMapper                                                              | Separate `@lazySingleton` mapper classes (NO `.toModel()` on DTO) |

## Standards

- Clean Architecture (Presentation -> Domain -> Data)
- Bloc for state management (never Cubit)
- **Pages MUST NOT call UseCases directly** — every async action (even logout/refresh/delete) goes through a Bloc. Pages only dispatch events and read state. Importing a UseCase or calling `getIt<XUseCase>()` from a page is ALWAYS wrong, no exceptions.
- Freezed for all models, states, events
- Injectable for DI (never manual getIt.register\*)
- Dio for networking — baseUrl set via NetworkModule, not in datasources
- **BOTH project types**: separate `@lazySingleton` mapper classes (`{Name}ModelMapper`, `{Action}ResultMapper`, `{Action}RequestMapper`) — NEVER `.toModel()` on DTO, NEVER extension functions
- Modular: query → `Future<Result>` (Result contains `Failure` + data), action → `Future<Failure>` directly
- Modular error chain: DioException → DioErrorInterceptor → AppException → FailureHandlerMixin → Failure
- Single-module: repository returns `Future<Result<T>>` where `T` is the mapped domain model/output (mapper runs inside repo before wrapping in `Result.ok(...)`)
- Single-module error chain: DioException → DioErrorInterceptor → AppException → ErrorMapper mixin → Failure → wrapped in `Result.error(failure)`
- ScreenUtil axes are semantic: `.w` width, `.h` height, `.r` radius/square size, `.sp` text/icon size; empty gaps MUST use `N.verticalSpace`/`N.horizontalSpace` (never spacing-only `SizedBox(height: N.h)` / `SizedBox(width: N.w)`)
- **Colors MUST use generated `AppColors` from `flutter_gen`** — NEVER `Color(0xFF...)`, NEVER `Colors.red`/`Colors.blue`/`Colors.grey`, NEVER inline hex. Source of truth is `colors.xml` (Android-style XML consumed by flutter_gen → `colors.gen.dart`). Applies to BOTH project types — modular reads from `packages/presentation/feature_common/assets/colors/colors.xml` (regen via `melos run generate:assets`); single-module reads from `assets/colors/colors.xml` (regen via `dart run build_runner build -d`). Adding a new color = edit `colors.xml` first, regenerate, then use `AppColors.xxx`.
- Single-module: encrypt_shared_preferences for local storage
- Modular: SharedPreferences via `@preResolve` LocalModule in data_common

## Usage

```bash
# Quick start (local plugin directory)
cd /path/to/your-flutter-project
claude --plugin-dir /path/to/gm-aiagent-plugins/plugins/ufil

# Or add via marketplace (local)
/plugin marketplace add /path/to/gm-aiagent-plugins

# Or from GitHub
/plugin marketplace add ghozimahdi/gm-aiagent-plugins

# Install from marketplace
/plugin install ufil@gm-aiagent-plugins

# Scaffold new project
/ufil:init-project my_app --package com.example.app --modular
/ufil:init-project my_app --package com.example.app --single

# Generate feature module
/ufil:generate-module tenant
/ufil:generate-module payment --layer domain

# Create a single BLoC (3 files: bloc/event/state)
/ufil:create-bloc home
/ufil:create-bloc home --actions get_transaction,add_transaction --alert
/ufil:create-bloc property_detail --with-failure --actions get_property_detail,delete_property

# Plan a ticket BEFORE implementing (saves plan markdown)
/ufil:plan 123
/ufil:plan issues/456

# Implement using the saved plan (auto-detects scope + team mode)
/ufil:implement 123

# Commit with Conventional Commits
/ufil:commit
/ufil:commit fix login timeout issue

# Implement multiple features in parallel (auto-scales agents)
/ufil:implement-batch tenant payment
/ufil:implement-batch auth tenant notification

# Create pull request
/ufil:create-pr
/ufil:create-pr develop

# Manage RTK token-saving hook
/ufil:rtk-status
/ufil:rtk-activate
/ufil:rtk-deactivate

```
