---
name: implement
description: "Implement a feature following clean architecture. Use for end-to-end implementation from a saved plan or ticket."
argument-hint: "<ticket-id|feature-name>"
disable-model-invocation: true
---

Use the current user request as this skill's input. In Claude Code invoke it as
`/ufil:implement`; in Codex invoke it as `$ufil:implement`. Resolve `UFIL_ROOT`
to the plugin root containing this skill; Claude Code may provide
`CLAUDE_PLUGIN_ROOT`, while Codex can resolve it from the installed skill path.
Use the client's native subagent capability; do not hardcode one client's tool
call schema.

Implement a feature following clean architecture.

Arguments: <requested arguments> (ticket ID or feature name)

## Project Type Detection (MUST DO FIRST)
- **Modular**: `packages/` directory exists → multi-package project with melos
- **Single-module**: No `packages/` directory → single `lib/` project

Steps:

1. **Load plan if it exists** — check `.ufil/plans/issue-<id>.md` in the target project when the requested scope is an issue ID. If found, read it and use its Scope Estimate + Implementation Plan as the source of truth. If not found, find the ticket/spec in project docs and understand requirements, flow, and data model.

## Step 1.5: Auto Team Mode Decision (MANDATORY before writing code)

After reading the ticket/spec, decide whether to use **single-agent sequential** or **team mode (parallel agents)**.

### Load team config

Read `${UFIL_ROOT}/config/team-config.json`. If the file does not exist or fails to parse, use these defaults:

```json
{
  "team": { "maxParallelAgents": 3, "useWorktreeIsolation": true, "splitStrategy": "by-layer-then-feature" },
  "autoTrigger": { "enabled": true, "rule": "any",
    "thresholds": { "pages": 3, "blocs": 3, "useCases": 3, "features": 2, "estimatedFiles": 15 } }
}
```

### Estimate scope from the ticket (or plan)

If a plan was loaded in Step 1, use its **Scope Estimate** table directly. Otherwise count from the ticket/spec:
- `pages` — number of distinct pages/screens to build
- `blocs` — number of distinct blocs (usually = pages, but can be shared)
- `useCases` — number of use cases (one per repository method called from blocs)
- `features` — number of distinct feature modules (e.g., `tenant` + `payment` = 2)
- `estimatedFiles` — rough total file count (models + DTOs + mappers + repos + datasources + blocs + pages + events + states + tests)

### Decide mode

Apply `autoTrigger.rule` against `autoTrigger.thresholds`:
- `any` (default) → switch to team mode if **any single count >= its threshold**
- `all` → require **every** count to meet its threshold
- `majority` → require **≥50%** of the counts to meet their thresholds

If `autoTrigger.enabled = false`, always use single-agent mode.

**Announce the decision to the user** in one line, e.g.:
```
Scope: 4 pages, 5 usecases, 1 feature, ~22 files → team mode (pages>=3 triggered).
```
or
```
Scope: 1 page, 2 usecases, 1 feature, ~8 files → single-agent mode.
```

### If team mode: execute the team flow inline

Do NOT ask the user to re-run a different command. Run this flow yourself:

1. **Architect phase** — read `${UFIL_ROOT}/agents/architect.md` as role guidance. In Claude Code, use the `gm-architect` agent when available. In Codex, spawn a general subagent with the same role guidance. Produce a structured plan:
   - List every file to be created/edited with full path and class name
   - Split work into **streams** using `team.splitStrategy`:
     - `by-layer-then-feature`: Stream A = domain+data (models, DTOs, mappers, repos, usecases, datasources). Stream B = presentation (blocs, events, states, pages, widgets). If presentation alone still exceeds threshold, split it into Stream B1 / B2 by page groups.
     - `by-feature-only`: one stream per feature; never split a single feature.
   - Mark inter-stream dependencies (Stream B depends on Stream A's contracts being defined).

2. **Parallel implementation phase** — read `${UFIL_ROOT}/agents/implementer.md` as role guidance and spawn one implementation subagent per stream (cap at `team.maxParallelAgents`; extras are batched sequentially):
   - Use worktree isolation when the client supports it and `team.useWorktreeIsolation = true`
   - Launch independent subagents concurrently using the client's native delegation mechanism
   - Each agent prompt MUST include: project type (modular/single-module), the architect's plan for that stream, the implementation order (domain→data→presentation), and the verification steps

3. **Merge & verify** — after all agents complete:
   - Merge worktrees back to the working branch (if isolation was used)
   - Resolve conflicts in shared files (router, injector, melos workspace)
   - Run `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`
   - Run code generation, `dart fix --apply`, `dart format`, `dart analyze`
   - Fix ALL errors before reporting done

4. **Auto Review (MANDATORY)** — read `${UFIL_ROOT}/agents/reviewer.md` as role guidance, then use `gm-reviewer` in Claude Code or a general review subagent in Codex to audit all merged files:
   - Architecture violations (page calls UseCase directly, no Bloc; Cubit instead of Bloc; `.toModel()` on DTO; missing separate mapper class; manual `getIt.register*`; `try/catch` in datasource; missing `@JsonKey` on DTO field)
   - Naming conventions (`{Action}UseCase`, `{Name}DataSource`, `{Name}ModelMapper`, event suffix `Event`, handler camelCase, …)
   - Bloc compliance (init event present, sub-state unions with 4 variants, error variant carries `Failure`)
   - Quality (no `=>` for method bodies; ScreenUtil axes are correct; empty gaps use `N.verticalSpace`/`N.horizontalSpace`; no business logic in pages)
   - **Fix ALL critical and warning issues found** — re-spawn an implementer agent (or fix inline if small) before proceeding.

5. **Final Verify (MANDATORY after review fixes)** — re-run `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`, `dart fix --apply lib/`, formatter, and analyzer. Fix ALL errors and warnings introduced or surfaced by the review fixes. Never skip — review-driven edits often re-introduce lint/analyzer issues.

6. **Stop**. Do NOT execute the single-agent steps below — they have already been delegated to the parallel agents.

### If single-agent mode: continue below

Proceed with Step 0 (read docs) and the sequential layer-by-layer steps that follow.

## Step 0: Read these BEFORE writing code (MANDATORY)

Read in order from the plugin's `${UFIL_ROOT}/docs/` directory:

1. `${UFIL_ROOT}/docs/NAMING_CONVENTIONS.md` — class/file suffixes (`UseCase`, `DataSource`, `Mapper`, …)
2. `${UFIL_ROOT}/docs/BLOC_PATTERN.md` — event/state shape, sub-state unions, init event
3. `${UFIL_ROOT}/docs/DOMAIN_LAYER.md` — Model / Params / Result rules
4. `${UFIL_ROOT}/docs/DATA_LAYER.md` — DTO / Response / Request rules, datasource, repo impl
5. `${UFIL_ROOT}/docs/MAPPERS.md` — separate mapper class rules (apply to BOTH project types)
6. `${UFIL_ROOT}/docs/SCREENUTIL.md` — responsive dimensions and mandatory spacing-axis rules

Do NOT proceed until all six are read. The body below is a summary; the docs are authoritative.

## Naming Suffixes (apply to BOTH project types)

- Domain model: `{Name}Model` — file `{name}_model.dart`
- DTO: `{Name}Dto` — file `{name}_dto.dart`
- Response: `{Action}Response` — file `{action}_response.dart`
- Request: `{Action}Request` — file `{action}_request.dart`
- Params: `{Action}Params` — file `{action}_params.dart`
- Result: `{Action}Result` — file `{action}_result.dart`
- Use case: `{Action}UseCase` — file `{action}_use_case.dart`  ← NEVER `Usecase` / `_usecase.dart`
- Data source: `{Name}DataSource` — file `{name}_data_source.dart`  ← NEVER `Datasource` / `_datasource.dart`
- Mapper: `{Name}ModelMapper` / `{Action}ResultMapper` / `{Action}RequestMapper` — file `{name}_mapper.dart`
- Bloc/Event/State: `{Feature}Bloc` / `{Feature}Event` / `{Feature}State`

## Bloc Pattern (apply to BOTH project types)

- **Pages MUST NOT call UseCases directly (NON-NEGOTIABLE).** Every async action goes through a Bloc — even one-shot ops like `logout`, `refresh`, `delete`, `markAsRead`. The page only does `context.read<TBloc>().add(event)` to dispatch and `BlocBuilder`/`BlocConsumer`/`BlocSelector`/`BlocListener` to read. A page that imports a UseCase or calls `getIt<XUseCase>()` is ALWAYS wrong. Fix: add sub-state class for the action → add event → inject the UseCase into the Bloc constructor → dispatch from the page. Navigation/snackbar happens in `BlocListener`, not in `onPressed`.
- Event redirects MUST suffix `Event`: `_InitEvent`, `_SubmittedEvent`, `_EmailChangedEvent`
- `init` event is MANDATORY: `const factory {Feature}Event.init({@Default({Feature}State()) {Feature}State state}) = _InitEvent;`
- Page must dispatch `add(const {Feature}Event.init())` in `BlocProvider.create`
- **Handler naming**: `_InitEvent` → `_initEvent`, `_GetTransactionEvent` → `_getTransactionEvent`, `_SubmittedEvent` → `_submittedEvent`. Handler is camelCase of the event class name (leading `_` kept, first letter lowercased, `Event` suffix kept). NEVER `_onX` / `_onXEvent` / `_handleX`.
- Each async action gets its own sub-state class with EXACTLY 4 variants: `idle`, `loading`, `done`, `error`
- Sub-state redirect classes: `{Action}IdleState`, `{Action}LoadingState`, `{Action}DoneState`, `{Action}ErrorState` (idle is private `_` prefix)
- Failure carried in error variant via `@Default(Failure.noFailure()) Failure failure` — applies to BOTH project types

## Mapper Layer (apply to BOTH project types)

- DTOs: `@freezed` + nullable fields + `@JsonKey(name: '...')` on EVERY field + `fromJson` factory. NO `.toModel()` — mappers are SEPARATE classes.
- Mappers: `@lazySingleton` `{Name}ModelMapper` with `mapFromData({Name}Dto? data)`
- Result mapper: `@lazySingleton` `{Action}ResultMapper` with `mapFromData({Action}Response? data)` — composes ModelMappers
- Request mapper: `@lazySingleton` `{Action}RequestMapper` with `mapFromDomain({Action}Params params)` — only when there's a request body
- **No private sanitizer helpers** (`_nullIfEmpty`, `_nullIfZero`, `_formatDate`, …) inside a mapper. Two canonical files:
  - `nullable_extensions.dart` — for mappers/repos/use cases. Modular: `packages/data/data_common/lib/src/extensions/nullable_extensions.dart`. Single-module: `lib/core/extensions/nullable_extensions.dart`. API: `.orEmpty()` / `.orZero()` / `.orFalse()` to default a nullable; `.orNull()` to collapse empty/zero to null; `.toIsoDate()` for `DateTime?`.
  - `dash_extensions.dart` — UI display only. Modular: `packages/presentation/feature_common/lib/src/extensions/dash_extensions.dart`. Single-module: `lib/core/extensions/dash_extensions.dart`. API: `.orDash()` returns `"-"` when empty/null, else the value as `String`.
  Never call `.orDash()` inside a mapper. Never call `.orNull()` directly in a `Text(...)`. Add new variants to the canonical file in the same change; never copy/paste helpers across mappers or widgets.
- Repository injects mapper(s) + datasource and calls mapper INSIDE the repo
- Even for typed SDKs (Supabase, Firestore): wrap return values in DTO so the boundary stays vendor-neutral

## Single-module Steps

2. **Domain layer** (`lib/features/<feature>/domain/`):
   - Models: `@freezed` + `@Default()` fields, no nullable. Any `DateTime` field → `required DateTime` + `.empty()` factory returning `DateTime.now()` for each DateTime.
   - Params: `@freezed` only when ≥4 fields (use named params for 1-3). Same DateTime rule applies — `required DateTime` + `.empty()` factory.
   - Result: `@freezed` containing the data shape (does NOT carry `Failure` — `Result<T>` wraps it)
   - Repository contract: abstract class returning `Future<Result<T>>` where `T` is a domain Result/Model
   - UseCases: `@lazySingleton`, plain `call()` method, return type matches repo

3. **Data layer** (`lib/features/<feature>/data/`):
   - DTOs / Responses / Requests: `@freezed` + nullable fields + `@JsonKey(name: '...')` on EVERY field, NO `.toModel()`
   - Mappers: separate `@lazySingleton` classes — `{Name}ModelMapper`, `{Action}ResultMapper`, `{Action}RequestMapper`
   - Data source: `@lazySingleton`, injects `Dio` only (baseUrl set via NetworkModule), raw API/DB calls, NO try/catch — returns Response/DTO
   - Repository impl: `@LazySingleton(as: Contract)`, `with ErrorMapper`, injects mapper(s) + datasource, calls mapper inside try, `catch (e) -> Result.error(mapToFailure(e))`

4. **Presentation layer** (`lib/features/<feature>/presentation/`):
   - Events + States: `@freezed abstract class`, sub-state unions per async action, init event mandatory, error variant carries `Failure failure`
   - Bloc: `@injectable`, one per page, `switch` on `Result` (Ok/Error), unwrap `error` into sub-state's `failure` field
   - Page: `@RoutePage()`, `BlocProvider` with `getIt<>()`; use `.w` for width, `.h` for height, `.r` for radius/square size, `.sp` for text/icon size, and `N.verticalSpace`/`N.horizontalSpace` for empty gaps

## Modular Steps

2. **Domain layer** (`packages/domain/domain_<feature>/`):
   - Models: `@freezed` + `@Default()` fields, no nullable. Any `DateTime` field → `required DateTime` + `.empty()` factory returning `DateTime.now()` for each DateTime.
   - Params: `@freezed` only when ≥4 fields (use named params for 1-3). Same DateTime rule applies — `required DateTime` + `.empty()` factory.
   - Result models: `@freezed` containing `@Default(Failure.noFailure()) Failure failure` + data (only for query methods that return data)
   - Repository contract: query → `Future<Result>`, action (no data) → `Future<Failure>`
   - UseCases: `@lazySingleton`, return type matches repo, plain `call()` method
   - Config: `Domain<Feature>Config extends AppConfig` + `di.dart`

3. **Data layer** (`packages/data/data_<feature>/`):
   - DTOs / Responses / Requests: `@freezed` + nullable fields + `@JsonKey(name: '...')` on EVERY field, NO `.toModel()`
   - Mappers: separate `@lazySingleton` classes — `{Name}ModelMapper`, `{Action}ResultMapper`, `{Action}RequestMapper` — using `mapFromData()` / `mapFromDomain()`
   - Data source: `@lazySingleton`, injects `Dio` only, raw API/DB calls, NO try/catch — returns Response/DTO
   - Repository impl: `@LazySingleton(as: Contract)`, `with FailureHandlerMixin`, query → injects ResultMapper + datasource, action → datasource only
   - Config: `Data<Feature>Config extends AppConfig` + `di.dart`

4. **Presentation layer** (`packages/presentation/feature_<feature>/`):
   - Events + States: `@freezed abstract class`, sub-state unions per async action, init event mandatory, error variant carries `@Default(Failure.noFailure()) Failure failure`
   - Bloc: `@injectable`, one per page, query → `switch` on `result.failure`, action → `switch` on `failure`
   - Page: `@RoutePage()`, `BlocProvider` with `getIt<>()`; use `.w` for width, `.h` for height, `.r` for radius/square size, `.sp` for text/icon size, and `N.verticalSpace`/`N.horizontalSpace` for empty gaps
   - Config: `Feature<Feature>Config extends AppConfig` + `di.dart`

## Shared Steps

5. **Wire up** — run code generation, register route
   - Modular: add package to workspace, add Config init to `app/lib/injector.dart`, add route to `app/lib/app_router.dart`
   - Non-modular: add route to `lib/app_router.dart`

6. **Verify (MANDATORY)** — run `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`, `dart fix --apply lib/`, analyzer, and formatter. Fix ALL errors and warnings. Never skip this step.

7. **Tests** — bloc test, repository test, usecase test, DTO test

8. **Auto Review (MANDATORY)** — read `${UFIL_ROOT}/agents/reviewer.md` as role guidance, then invoke the Claude `gm-reviewer` agent or a Codex review subagent to audit all files created/modified in this run:
   - Architecture violations (page calls UseCase directly, no Bloc; Cubit instead of Bloc; `.toModel()` on DTO; missing separate mapper class; manual `getIt.register*`; `try/catch` in datasource; missing `@JsonKey` on DTO field)
   - Naming conventions (`{Action}UseCase`, `{Name}DataSource`, `{Name}ModelMapper`, event suffix `Event`, handler camelCase, …)
   - Bloc compliance (init event present, sub-state unions with 4 variants, error variant carries `Failure`)
   - Quality (no `=>` for method bodies; ScreenUtil axes are correct; empty gaps use `N.verticalSpace`/`N.horizontalSpace`; no business logic in pages)
   - **Fix ALL critical and warning issues found** before proceeding.

9. **Final Verify (MANDATORY after review fixes)** — re-run `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`, `dart fix --apply lib/`, formatter, and analyzer. Fix ALL errors and warnings introduced or surfaced by the review fixes. Never skip this step — review-driven edits often re-introduce lint/analyzer issues.

## Team Mode (auto-triggered)

Team mode is decided in **Step 1.5** above based on `${UFIL_ROOT}/config/team-config.json`. Once team mode is selected, do NOT run the single-agent steps in this file — delegate to the architect + parallel implementer flow described in Step 1.5.

To change thresholds, max parallel agents, or split strategy, edit `team-config.json` directly. To disable auto team mode, set `autoTrigger.enabled = false`.

## References

Plugin docs live under the resolved `UFIL_ROOT`. Do NOT substitute similarly named project documentation for these references.

- `${UFIL_ROOT}/docs/ARCHITECTURE.md` — Clean Architecture overview, modular vs single-module
- `${UFIL_ROOT}/docs/DOMAIN_LAYER.md` — Domain layer patterns and conventions
- `${UFIL_ROOT}/docs/DATA_LAYER.md` — Data layer patterns, DTOs, datasources
- `${UFIL_ROOT}/docs/PRESENTATION_LAYER.md` — Presentation layer, pages, widgets
- `${UFIL_ROOT}/docs/BLOC_PATTERN.md` — Bloc events, states, sub-state unions
- `${UFIL_ROOT}/docs/NAMING_CONVENTIONS.md` — File and class naming standards
- `${UFIL_ROOT}/docs/CODE_STYLE.md` — Import ordering and code formatting
- `${UFIL_ROOT}/docs/MAPPERS.md` — Mapper creation rules (apply to BOTH project types)
- `${UFIL_ROOT}/docs/SCREENUTIL.md` — Responsive dimensions, spacing helpers, and axis rules
