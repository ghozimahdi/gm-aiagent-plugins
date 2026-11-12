---
name: implement-batch
description: "Implement multiple features in parallel using multiple agents. Auto-scales based on task count."
argument-hint: "<feature-1> [feature-2] [...]"
disable-model-invocation: true
---

Use the current user request as this skill's input. In Claude Code invoke it as
`/ufil:implement-batch`; in Codex invoke it as `$ufil:implement-batch`. Resolve
`UFIL_ROOT` to the plugin root containing this skill; Claude Code may provide
`CLAUDE_PLUGIN_ROOT`, while Codex can resolve it from the installed skill path.
Use the client's native subagent capability; do not hardcode one client's tool
call schema.

Implement multiple features in parallel using auto-scaled agents.

Arguments: <requested arguments> (space-separated feature names or ticket IDs)

## Project Type Detection (MUST DO FIRST)

- **Modular**: `packages/` directory exists → multi-package project with melos
- **Single-module**: No `packages/` directory → single `lib/` project

## Load team config (MUST DO BEFORE PHASE 2)

Read `${UFIL_ROOT}/config/team-config.json` to load:

- `team.maxParallelAgents` — hard cap on parallel agents (default 3)
- `team.useWorktreeIsolation` — whether to use worktree isolation when the client supports it (default true)
- `team.splitStrategy` — how to split work when streams exceed the cap (default `by-layer-then-feature`)

If the file is missing or malformed, fall back to defaults: `maxParallelAgents=3`, `useWorktreeIsolation=true`, `splitStrategy=by-layer-then-feature`.

## Phase 1 — Analyze & Plan (Architect)

Read `${UFIL_ROOT}/agents/architect.md` as role guidance. Use the Claude `gm-architect` agent when available, or spawn a general Codex subagent with that guidance, to:

1. Parse the list of features/tickets from the arguments
2. For each feature, define: models, DTOs, repos, usecases, blocs, pages
3. Identify **dependencies between features** (shared models, common repos, etc.)
4. Group features into **independent work streams** that can run in parallel

Output a structured plan:

```
Stream 1: [feature_a] — no dependencies
Stream 2: [feature_b] — no dependencies
Stream 3: [feature_c, feature_d] — feature_d depends on feature_c's model
```

## Phase 2 — Auto-Scale Agent Count

Based on the number of **independent work streams** from Phase 1 and `team.maxParallelAgents` (call it `N`) from the config:

| Independent Streams | Agents to Spawn | Strategy                                           |
| ------------------- | --------------- | -------------------------------------------------- |
| 1                   | 1 agent         | Sequential — single implementer                    |
| 2..N                | streams agents  | Parallel — each in worktree isolation (if enabled) |
| > N                 | N agents (max)  | Parallel — batch extra streams across the N agents |

**Rules:**

- Maximum **`team.maxParallelAgents`** parallel agents (default 3) — more causes diminishing returns and merge conflicts
- Features with **dependencies** go into the **same stream** (same agent, sequential)
- Features that are **independent** go into **separate streams** (separate agents, parallel)
- Each parallel agent uses **worktree isolation** when `team.useWorktreeIsolation = true`

## Phase 3 — Parallel Implementation

Read `${UFIL_ROOT}/agents/implementer.md` as role guidance. For each work stream, use the Claude `gm-implementer` agent when available, or spawn a general Codex subagent with that guidance. Use worktree isolation when supported and enabled.

Each agent's prompt MUST include:

1. The detected **project type** (modular or single-module)
2. The **specific features** assigned to that stream
3. The **architect's plan** for those features (file paths, class names, signatures)
4. The **implementation order**: domain → data → presentation
5. Instruction to run code generation and verification after implementation

### Subagent prompt template

For each stream, use the client's native delegation mechanism with this prompt:

```
You are implementing Flutter features using Clean Architecture.

Project type: <modular|single-module>

## Features to implement:
<architect's plan for this stream>

## Implementation order:
1. Domain models (@freezed, @Default, no nullable)
2. Repository contracts (abstract class)
3. UseCases (@lazySingleton, plain call())
4. DTOs (@freezed, nullable, @JsonKey on EVERY field, .toModel())
5. Datasources (@lazySingleton, Dio only, NO try/catch)
6. Repository impls (@LazySingleton(as:), with error handler mixin)
7. Bloc events + states (@freezed abstract class, sub-state unions)
8. Bloc (@injectable, part/part of structure)
9. Pages + Widgets (@RoutePage, BlocProvider, ScreenUtil; empty gaps use N.verticalSpace/N.horizontalSpace)

## After writing code:
1. Run code generation
2. Run ${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test
3. Run dart fix --apply lib/
4. Run dart format lib/
5. Run dart analyze — fix ALL errors

## Mandatory rules:
- Always Bloc, never Cubit
- @injectable for DI
- No try/catch in datasources
- Freezed everywhere
- @JsonKey on every DTO field
- No arrow (=>) for method bodies
- Empty vertical/horizontal gaps use `N.verticalSpace`/`N.horizontalSpace`; never spacing-only `SizedBox(height: N.h)` or `SizedBox(width: N.w)`
- Sub-state freezed unions, never flat bool flags
- Modular: FailureHandlerMixin, query → Future<Result> (Failure + data), action → Future<Failure>, separate mapper classes
- Single-module: ErrorMapper + Result<T>
```

Launch independent subagents concurrently. Keep dependent streams sequential.

## Phase 4 — Merge & Verify

After all agents complete:

1. Review each agent's worktree changes
2. If using worktrees, merge changes back to the working branch
3. Resolve any conflicts (shared files like router, injector)
4. Run full verification:
   - `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`
   - Modular: `melos run build`
   - Single: `fvm dart run build_runner build --delete-conflicting-outputs`
5. Run `fvm dart fix --apply lib/`
6. Run `fvm dart format lib/`
7. Run `fvm dart analyze` — fix ALL errors

## Phase 4.5 — Auto Review (MANDATORY)

After merge & verify pass, read `${UFIL_ROOT}/agents/reviewer.md` as role guidance. Use the Claude `gm-reviewer` agent or one Codex review subagent to audit ALL files created/modified across every stream:

- Architecture violations: page calls UseCase directly (no Bloc), Cubit instead of Bloc, `.toModel()` on DTO, missing separate mapper class, manual `getIt.register*`, `try/catch` in datasource, missing `@JsonKey` on DTO field
- Naming conventions: `{Action}UseCase`, `{Name}DataSource`, `{Name}ModelMapper`, event suffix `Event`, handler camelCase
- Bloc compliance: init event present, sub-state unions with 4 variants, error variant carries `Failure`
- Quality: no `=>` for method bodies; ScreenUtil axes are correct; empty gaps use `N.verticalSpace`/`N.horizontalSpace`; no business logic in pages

**Fix ALL critical and warning issues found.** If an issue is large, delegate it back to an implementation subagent for that stream; if small, fix inline.

## Phase 4.6 — Final Verify (MANDATORY after review fixes)

After review fixes, re-run the full verification pass:

1. Modular: `melos run build` — Single: `fvm dart run build_runner build --delete-conflicting-outputs`
2. `${UFIL_ROOT}/scripts/check-screenutil-spacing.sh lib packages test`
3. `fvm dart fix --apply lib/`
4. `fvm dart format lib/`
5. `fvm dart analyze` — fix ALL errors and warnings

Never skip this — review-driven edits frequently re-introduce lint/analyzer issues.

## Phase 5 — Summary

Report to user:

- Number of agents used
- Features implemented per agent
- Any conflicts resolved
- Verification status (analyzer clean or issues remaining)
- Review status (issues found / fixed / remaining)

## Examples

```text
# 2 independent features → 2 parallel agents
Claude: /ufil:implement-batch tenant payment
Codex:  $ufil:implement-batch tenant payment

# 3 features → 3 parallel agents
Claude: /ufil:implement-batch auth tenant notification
Codex:  $ufil:implement-batch auth tenant notification

# 4 features → 3 agents (batched)
Claude: /ufil:implement-batch auth tenant payment notification
Codex:  $ufil:implement-batch auth tenant payment notification

# Features with dependency → grouped in same agent
Claude: /ufil:implement-batch order order-history
Codex:  $ufil:implement-batch order order-history
# → 1 agent (order-history depends on order models)
```

## References

- `${UFIL_ROOT}/docs/ARCHITECTURE.md` — Clean Architecture overview
- `${UFIL_ROOT}/docs/DOMAIN_LAYER.md` — Domain layer patterns
- `${UFIL_ROOT}/docs/DATA_LAYER.md` — Data layer patterns
- `${UFIL_ROOT}/docs/PRESENTATION_LAYER.md` — Presentation layer
- `${UFIL_ROOT}/docs/BLOC_PATTERN.md` — Bloc patterns
- `${UFIL_ROOT}/docs/SCREENUTIL.md` — Responsive dimensions, spacing helpers, and axis rules
