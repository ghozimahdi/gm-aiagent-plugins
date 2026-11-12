---
name: plan
description: "Analyze a GitHub issue/ticket and create a Flutter implementation plan markdown before coding."
argument-hint: "<issue-id>"
disable-model-invocation: true
---

Use the current user request as this skill's input. In Claude Code invoke it as
`/ufil:plan`; in Codex invoke it as `$ufil:plan`. Resolve `UFIL_ROOT` to the
plugin root containing this skill; Claude Code may provide
`CLAUDE_PLUGIN_ROOT`, while Codex can resolve it from the installed skill path.
Use the client's native subagent capability; do not hardcode one client's tool
call schema.

Analyze a GitHub issue/ticket and create a detailed Flutter implementation plan BEFORE coding.

Arguments: <requested arguments> (GitHub issue ID, e.g., `123` or `issues/123`)

## Step 0: Read docs (MANDATORY)

### 0a. Project Type Detection

- **Modular**: `packages/` directory exists at project root → multi-package project with melos
- **Single-module**: No `packages/` directory → single `lib/` project

### 0b. Read plugin docs

Read from `${UFIL_ROOT}/docs/`:

1. `${UFIL_ROOT}/docs/ARCHITECTURE.md`
2. `${UFIL_ROOT}/docs/NAMING_CONVENTIONS.md`
3. `${UFIL_ROOT}/docs/BLOC_PATTERN.md`
4. `${UFIL_ROOT}/docs/DOMAIN_LAYER.md`
5. `${UFIL_ROOT}/docs/DATA_LAYER.md`
6. `${UFIL_ROOT}/docs/PRESENTATION_LAYER.md`
7. `${UFIL_ROOT}/docs/MAPPERS.md`

Also read relevant project guidelines from `docs/` in the working directory (if present).

Do NOT proceed until docs are read.

## Steps

### 1. Fetch & understand the issue

Extract issue ID from `<requested arguments>` (strip `issues/` prefix if present, strip `#` prefix).

Detect the GitHub repo from the local git remote, then fetch:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh issue view <issue_id> --repo "$REPO" --json title,body,labels,assignees,milestone,comments
```

Read and understand:
- **What** is being requested (feature, bug fix, refactor, etc.)
- **Why** it's needed (business context, user impact)
- **Acceptance criteria** (explicit or implied)
- **Constraints** (deadlines, dependencies, related issues)
- **API/data contracts** referenced (endpoints, schemas, sample payloads)

If the issue references other issues or PRs, fetch those too for context.

### 2. Scope estimation (feeds Step 1.5 of the `implement` skill)

From the issue, count:
- `pages` — distinct screens to build
- `blocs` — distinct blocs (usually = pages, sometimes shared)
- `useCases` — one per repository method called from blocs
- `features` — distinct feature modules touched
- `estimatedFiles` — rough total (models + DTOs + mappers + repos + datasources + blocs + pages + events + states + tests)

Record these in the plan so the `implement` skill can decide single-agent vs team mode from `${UFIL_ROOT}/config/team-config.json` without recounting.

### 3. Explore the codebase

Based on the issue and project type, explore relevant parts:

**Modular projects** — for each affected feature, check:
- `packages/domain/domain_<feature>/` — existing models, repo contracts, usecases, `di.dart`
- `packages/data/data_<feature>/` — existing DTOs, datasources, repo impls, mappers
- `packages/presentation/feature_<feature>/` — existing blocs, pages, widgets
- `app/lib/injector.dart` — config wiring
- `app/lib/app_router.dart` — route registration
- root `pubspec.yaml` — `workspace:` list (package paths) and `melos:` scripts

**Single-module projects** — check:
- `lib/features/<feature>/domain/` — models, repos, usecases
- `lib/features/<feature>/data/` — DTOs, datasources, repo impls, mappers
- `lib/features/<feature>/presentation/` — blocs, pages, widgets
- `lib/core/` — shared error/result/network
- `lib/injector.dart` — DI registration
- `lib/app_router.dart` — routes

For complex architecture decisions or a feature with 3+ pages or 3+ use cases, read `${UFIL_ROOT}/agents/architect.md` as role guidance. Use the Claude `gm-architect` agent or a general Codex subagent with that guidance.

### 4. Create the plan

Create a plan markdown file inside the target project's UFIL workspace:

```
.ufil/plans/issue-<issue_id>.md
```

If `.ufil/plans/` doesn't exist, create it.

Plans live in the target project so they remain writable after marketplace installation and are picked up by both clients' `implement` skill.

### Plan Template

The plan MUST follow this structure:

```markdown
# Issue #<issue_id>: <issue title>

> Source: <GitHub issue URL>
> Created: <date>
> Status: Draft
> Project type: <modular | single-module>

## Summary

<1-3 sentences explaining what needs to be done and why>

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>

## Scope Estimate

| Metric | Count |
|--------|-------|
| pages | N |
| blocs | N |
| useCases | N |
| features | N |
| estimatedFiles | N |

> Used by the `implement` skill Step 1.5 to decide single-agent vs team mode.

## Analysis

### Affected Areas

**Modular projects:**

| Package | Files/Components | Impact |
|---------|------------------|--------|
| `domain_<feature>` | models, repo contract, usecases, di.dart | New/Modified |
| `data_<feature>` | DTOs, mappers, datasource, repo impl, di.dart | New/Modified |
| `feature_<feature>` | bloc, events, states, page, widgets, di.dart | New/Modified |
| `app` | injector.dart, app_router.dart | Modified |

**Single-module projects:**

| Layer | Files/Components | Impact |
|-------|------------------|--------|
| Domain | `lib/features/<f>/domain/...` | New/Modified |
| Data | `lib/features/<f>/data/...` | New/Modified |
| Presentation | `lib/features/<f>/presentation/...` | New/Modified |
| App | `lib/injector.dart`, `lib/app_router.dart` | Modified |

### Existing Code Context

<Key findings from codebase exploration — existing models, blocs, repos that this feature relates to or reuses>

### Dependencies

- <Related issues, PRs, or features this depends on or blocks>
- <External SDKs/APIs introduced (Dio endpoints, Supabase tables, Firestore collections)>

## Implementation Plan

### 1. Domain Layer

- **Models** (`{Name}Model`, `@freezed`, `@Default()`, no nullable):
  - `<ModelName>` — fields: `<field:type>`
- **Params** (`{Action}Params`, only if ≥4 fields):
  - `<ActionParams>` — fields
- **Result** (`{Action}Result`, `@freezed`):
  - Modular: contains `@Default(Failure.noFailure()) Failure failure` + data
  - Single-module: contains data only (`Result<T>` wraps it)
- **Repository contract** (abstract class):
  - Modular: query → `Future<Result>`, action → `Future<Failure>`
  - Single-module: `Future<Result<T>>`
- **UseCases** (`@lazySingleton`, plain `call()`):
  - `<ActionUseCase>` — returns `<ReturnType>`

### 2. Data Layer

- **DTOs / Responses / Requests** (`@freezed`, nullable, `@JsonKey(name: '...')` on EVERY field):
  - `<Name>Dto`, `<Action>Response`, `<Action>Request`
- **Mappers** (`@lazySingleton`, separate classes — NEVER `.toModel()`):
  - `<Name>ModelMapper` — `mapFromData(<Name>Dto?)`
  - `<Action>ResultMapper` — `mapFromData(<Action>Response?)`
  - `<Action>RequestMapper` — `mapFromDomain(<Action>Params)` (only if request body)
- **Data source** (`@lazySingleton`, Dio only, NO try/catch):
  - `<Name>DataSource` — endpoints/methods
- **Repository impl** (`@LazySingleton(as: Contract)`):
  - Modular: `with FailureHandlerMixin`
  - Single-module: `with ErrorMapper`

### 3. Presentation Layer

- **Events** (`@freezed abstract class`, `Event` suffix on every redirect):
  - `_InitEvent` (MANDATORY, `@Default(<Feature>State()) state`)
  - `_<Action>Event` per async action
- **States** (`@freezed abstract class`, sub-state union per async action):
  - `<Action>IdleState`, `<Action>LoadingState`, `<Action>DoneState`, `<Action>ErrorState`
  - Error state carries `@Default(Failure.noFailure()) Failure failure`
- **Bloc** (`@injectable`, one per page):
  - Injected: `<usecases>`
  - Handlers: `_initEvent`, `_<action>Event` (camelCase of event class)
- **Page** (`@RoutePage()`, `BlocProvider`, ScreenUtil):
  - `<Feature>Page` — dispatches `init` event in `BlocProvider.create`

### 4. DI Wiring

- Modular: add `<Feature>Config extends AppConfig` + `di.dart` per package, register in `app/lib/injector.dart`
- Single-module: add to `lib/injector.dart`

### 5. Routing

- Add route to `app_router.dart` (modular: `app/lib/`; single: `lib/`)

### 6. Tests

- Bloc test (per bloc, all events)
- Repository test (mapper + datasource integration)
- UseCase test (delegates to repo)
- DTO test (`fromJson` / `toJson` round-trip)

## Implementation Order

1. [ ] Domain models + Params + Result
2. [ ] Repository contract + UseCases
3. [ ] DTOs + Mappers
4. [ ] Data source
5. [ ] Repository impl
6. [ ] Bloc events + states
7. [ ] Bloc
8. [ ] Page + Widgets
9. [ ] DI wiring (Config + di.dart) + Route
10. [ ] Code generation (`melos run build` or `dart run build_runner`)
11. [ ] `dart fix --apply` + `dart format` + `dart analyze`
12. [ ] Tests

## Risks & Notes

- <Potential issues, edge cases, shared bloc state concerns>
- <Questions that need clarification from team>
- <Performance concerns (large lists, network bursts, image-heavy pages)>
```

### 5. Present the plan

After creating the file, display:
- The full plan to the user
- The file path: `.ufil/plans/issue-<issue_id>.md`
- Ask if the plan looks good or needs adjustments

Tell the user:
```
Plan saved to .ufil/plans/issue-<issue_id>.md

When ready to implement, run:
  Claude Code: /ufil:implement <issue_id>
  Codex: $ufil:implement <issue_id>

The `implement` skill will load this plan and use the Scope Estimate to decide
single-agent vs team mode (per config/team-config.json).
```

## Important Rules

- **DO NOT write any implementation code** — this is planning only
- **DO explore the codebase thoroughly** (Dart LSP, Grep, Glob, Read) — the plan must be grounded in real symbols/files
- **DO check naming conventions** — class/file suffixes (`UseCase`, `DataSource`, `Mapper`, `Bloc`, …) must follow project standards
- **DO identify ALL affected packages** (modular) or feature folders (single-module)
- **Pages MUST NOT call UseCases directly** — every async action goes through a Bloc, even one-shot ops like logout/refresh/delete
- **Separate mapper classes** — NEVER `.toModel()` on DTO, NEVER extension functions
- **Modular**: query → `Future<Result>` (Failure + data), action → `Future<Failure>`
- **Single-module**: repo returns `Future<Result<T>>` with mapped domain model

## References

- `${UFIL_ROOT}/docs/ARCHITECTURE.md` — Clean Architecture overview
- `${UFIL_ROOT}/docs/NAMING_CONVENTIONS.md` — File and class naming
- `${UFIL_ROOT}/docs/DOMAIN_LAYER.md` — Domain patterns
- `${UFIL_ROOT}/docs/DATA_LAYER.md` — Data patterns
- `${UFIL_ROOT}/docs/PRESENTATION_LAYER.md` — Presentation patterns
- `${UFIL_ROOT}/docs/BLOC_PATTERN.md` — Bloc events, states, sub-state unions
- `${UFIL_ROOT}/docs/MAPPERS.md` — Mapper rules
- `${UFIL_ROOT}/config/team-config.json` — team mode thresholds
