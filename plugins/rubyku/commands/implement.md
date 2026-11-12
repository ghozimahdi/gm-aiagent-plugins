---
description: "Implement a feature following Rails Way architecture. The main orchestration command."
argument-hint: "[issue-id or feature-name]"
allowed-tools: ["Read", "Edit", "Write", "Bash", "Glob", "Grep", "Agent", "Skill"]
---

Implement a feature following Rails Way architecture.

Arguments: $ARGUMENTS (GitHub issue ID or feature name)

## Step 0: Read docs (MANDATORY)

### 0a. Read plugin docs

Read in order from the plugin's `${CLAUDE_PLUGIN_ROOT}/docs/` directory (resolve `$CLAUDE_PLUGIN_ROOT` via `echo $CLAUDE_PLUGIN_ROOT` first):

1. `${CLAUDE_PLUGIN_ROOT}/docs/ARCHITECTURE.md` — layers, patterns
2. `${CLAUDE_PLUGIN_ROOT}/docs/NAMING_CONVENTIONS.md` — naming rules
3. `${CLAUDE_PLUGIN_ROOT}/docs/CODE_OF_CONDUCT.md` — coding standards
4. `${CLAUDE_PLUGIN_ROOT}/docs/HOTWIRE.md` — Turbo/Stimulus patterns
5. `${CLAUDE_PLUGIN_ROOT}/docs/ROUTES_POLICY.md` — RESTful routes

Also read relevant project guidelines from `docs/guidelines/` in the working directory.

Do NOT proceed until docs are read.

## Steps

### 1. Check for existing plan

Extract issue ID from `$ARGUMENTS` (strip `issues/` prefix or `#` prefix if present).

Resolve the plugin root: `echo $CLAUDE_PLUGIN_ROOT`

Check if a plan exists in the **plugin directory**:

```bash
ls ${CLAUDE_PLUGIN_ROOT}/docs/plans/issue-<issue_id>.md 2>/dev/null
```

- **If plan exists**: Read `${CLAUDE_PLUGIN_ROOT}/docs/plans/issue-<issue_id>.md` and use it as the implementation blueprint. Skip step 3 (Architect planning) — the plan already has the design.
- **If plan does NOT exist**: Continue to step 2 for on-the-fly planning.

Also check for related specs: `docs/specifications/` and `docs/plans/` in the project directory.

### 2. Understand requirements

- If `$ARGUMENTS` is an issue ID, fetch the issue: `gh issue view $ARGUMENTS` (`gh` auto-detects the repo from the current git checkout)
- Read related specs in `docs/specifications/` or `docs/plans/`
- Understand the feature scope, affected namespaces, and data model

### 2.5. Auto-fanout check (MANDATORY before planning)

Before running the Architect, perform a **fast scope assessment** to decide whether this issue should be implemented as a single stream or fanned out via `/implement-batch`.

Count the following from the issue body, specs, and any existing plan:

- **Independent features** — distinct user-facing capabilities that share no model/route changes
- **New top-level models** — models that don't `belongs_to` each other
- **Affected namespaces** — distinct top-level route prefixes the host app uses (`/admin`, `/api`, and any role-specific prefixes like `/s`, `/c`, `/t`)

**Decision matrix:**

| Signal | Action |
|--------|--------|
| 1 feature, 1 namespace, ≤2 new models | **Stay in `/implement`** (single stream) |
| ≥2 independent features (no shared model/route) | **Redirect to `/implement-batch`** |
| ≥3 unrelated new top-level models | **Redirect to `/implement-batch`** |
| ≥3 namespaces touched with independent screens | **Redirect to `/implement-batch`** |
| Features share migrations / routes / models | **Stay in `/implement`** — fanout would conflict |

**If redirect is triggered:**
1. Print: `🔀 Detected N independent streams — switching to /implement-batch flow (max 3 parallel agents).`
2. List the streams you identified.
3. Ask the user for one-line confirmation: `Proceed with batch mode? [Y/n]`
4. On `Y` (or empty) → follow `${CLAUDE_PLUGIN_ROOT}/commands/implement-batch.md` from Phase 1 onward, passing the identified stream list.
5. On `n` → continue with single-stream flow below.

**If staying single-stream:** continue to step 3.

### 3. Plan (use Architect agent — skip if plan exists from step 1)

Use the **rubyku-architect** agent to:
- Design models, concerns, controllers, routes, views
- Create ordered implementation tasks
- Identify which namespace(s) are affected (`/admin`, `/api`, or any role-specific prefixes used by the host app)

### 4. Implement (follow this order)

1. **Migration** — `bin/rails generate migration Name`
   - Naming: `*_at` for datetime, `*_on` for date, no `is_`/`has_` booleans
   - Run `bin/rails db:migrate`

2. **Model** — validations, associations, concerns
   - Include `AttributeLabels`
   - Use `acts_as_paranoid` if soft deletes needed
   - Business logic in concerns, NOT service classes
   - Use enum with explicit integer values

3. **Routes** — RESTful resources only
   - New screen = new controller
   - State pages as nested namespace with resource
   - Add to correct namespace route file

4. **Controller** — THIN, HTTP flow only
   - Query through parent associations
   - Strong parameters
   - No business logic

5. **Views** — ERB with Hotwire
   - Turbo Frames for partial updates
   - `form.submit` (NOT `<button type="submit">`)
   - Rails form helpers (NOT raw HTML)
   - URL helpers (NOT hardcoded strings)
   - Tailwind CSS for styling

6. **Stimulus** — client-only UI behavior (if needed)
   - Correct namespace placement
   - No fetch calls for server communication

7. **Jobs** — Solid Queue background processing (if needed)
   - Name ending with `Job`
   - Inherit from `ApplicationJob`

8. **Mailers** — email notifications (if needed)
   - Name ending with `Mailer`

9. **I18n** — translations
   - Views: `config/locales/views/{namespace}/{controller}.{locale}.yml`
   - Models: `config/locales/models/`

10. **Tests** — Minitest
    - Model, controller, and system tests

### 5. Review (use Reviewer agent)

After implementation, use the **rubyku-reviewer** agent to audit all modified files:
- Architecture violations (thin controllers, no service classes, no display logic in models)
- Naming conventions (boolean, datetime, enum)
- Frontend compliance (Hotwire-first, no fetch, form helpers, helpers for display logic)
- Code quality (English comments, I18n, validations)

**Fix ALL critical and warning issues found before proceeding.**

### 6. Verify

1. `bundle exec rubocop <modified_files>` — fix ALL offenses
2. `bin/rails test <relevant_tests>` — all tests pass
3. Check all code comments are in English
4. Verify no service classes created
5. Verify controllers are thin
6. Verify query through parent associations
7. Verify display logic is in helpers, NOT models

## References

- `${CLAUDE_PLUGIN_ROOT}/docs/ARCHITECTURE.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/CODE_OF_CONDUCT.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/NAMING_CONVENTIONS.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/HOTWIRE.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/ROUTES_POLICY.md`
