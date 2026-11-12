---
description: "Analyze a GitHub issue/ticket, create an implementation plan markdown before coding."
argument-hint: "<issue-id>"
allowed-tools: ["Read", "Bash", "Glob", "Grep", "Agent"]
model: opus
---

Analyze a GitHub issue/ticket and create a detailed implementation plan BEFORE coding.

Arguments: $ARGUMENTS (GitHub issue ID, e.g., `123` or `issues/123`)

## Step 0: Read docs (MANDATORY)

### 0a. Read plugin docs

Read from `${CLAUDE_PLUGIN_ROOT}/docs/` (resolve via `echo $CLAUDE_PLUGIN_ROOT` first):

1. `${CLAUDE_PLUGIN_ROOT}/docs/ARCHITECTURE.md`
2. `${CLAUDE_PLUGIN_ROOT}/docs/NAMING_CONVENTIONS.md`
3. `${CLAUDE_PLUGIN_ROOT}/docs/CODE_OF_CONDUCT.md`
4. `${CLAUDE_PLUGIN_ROOT}/docs/HOTWIRE.md`
5. `${CLAUDE_PLUGIN_ROOT}/docs/ROUTES_POLICY.md`
6. `${CLAUDE_PLUGIN_ROOT}/docs/HELPERS.md`

Also read relevant project guidelines from `docs/guidelines/` in the working directory.

Do NOT proceed until docs are read.

## Steps

### 1. Fetch & understand the issue

Extract issue ID from `$ARGUMENTS` (strip `issues/` prefix if present, strip `#` prefix).

```bash
gh issue view <issue_id> --json title,body,labels,assignees,milestone,comments
```

Read and understand:
- **What** is being requested (feature, bug fix, refactor, etc.)
- **Why** it's needed (business context, user impact)
- **Acceptance criteria** (explicit or implied)
- **Constraints** (deadlines, dependencies, related issues)

If the issue references other issues or PRs, fetch those too for context.

### 2. Explore the codebase

Based on the issue, explore relevant parts of the codebase:

- **Models**: Check existing models, associations, concerns that are affected
- **Controllers**: Check existing controllers in the relevant namespace(s)
- **Routes**: Check `config/routes.rb` or namespace route files
- **Views**: Check existing views/partials that may need changes
- **Tests**: Check existing test coverage
- **Migrations**: Check recent migrations for related schema changes
- **Specs/Plans**: Check `docs/specifications/` and `docs/plans/` for related documents

Use the **rubyku-architect** agent for complex architecture decisions.

### 3. Create the plan

Resolve the plugin root first: `echo $CLAUDE_PLUGIN_ROOT`

Create a plan markdown file inside the **plugin directory** (NOT the project directory):

```
${CLAUDE_PLUGIN_ROOT}/docs/plans/issue-<issue_id>.md
```

If the `${CLAUDE_PLUGIN_ROOT}/docs/plans/` directory doesn't exist, create it.

**IMPORTANT**: Plans are stored in the plugin directory so they persist across sessions and are accessible by `/implement`.

### Plan Template

The plan MUST follow this structure:

```markdown
# Issue #<issue_id>: <issue title>

> Source: <GitHub issue URL>
> Created: <date>
> Status: Draft

## Summary

<1-3 sentences explaining what needs to be done and why>

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] ...

## Analysis

### Affected Areas

| Area | Files/Components | Impact |
|------|-----------------|--------|
| Models | `app/models/...` | New/Modified |
| Controllers | `app/controllers/...` | New/Modified |
| Views | `app/views/...` | New/Modified |
| Routes | `config/routes.rb` | Modified |
| Tests | `test/...` | New |

### Existing Code Context

<Key findings from codebase exploration — existing patterns, related models, current behavior>

### Dependencies

- <Related issues, PRs, or features that this depends on or blocks>

## Implementation Plan

### 1. Migration

```ruby
# Description of schema changes
# Table: <table_name>
# Columns: <column details with types and conventions>
```

### 2. Model

- **Model**: `ModelName`
  - Attributes: `name:string`, `status:integer`, ...
  - Associations: `belongs_to :parent`, `has_many :children`
  - Validations: `presence`, `uniqueness`, ...
  - Concerns: `ModelName::ConcernName` — <purpose>
  - Include: `AttributeLabels`, `acts_as_paranoid` (if needed)

### 3. Routes

```ruby
# Namespace and RESTful resources
namespace :x do
  resources :feature_name, only: [:index, :show, :new, :create]
end
```

### 4. Controller

- **Controller**: `Namespace::FeatureNameController`
  - Actions: `index`, `show`, `new`, `create`
  - Strong params: `[:field1, :field2]`
  - Query through: `current_user.association`

### 5. Views

- `index.html.erb` — <description, Turbo Frame usage>
- `show.html.erb` — <description>
- `_form.html.erb` — <form helpers, fields>
- `_item.html.erb` — <partial with dom_id>

### 6. Helpers (if display logic needed)

- `app/helpers/feature_name_helper.rb`
  - `method_name(arg)` — <what it formats/displays>

### 7. Stimulus (if client-side behavior needed)

- `app/javascript/controllers/namespace/controller_name_controller.js`
  - Targets, values, actions

### 8. Jobs (if background processing needed)

- `FeatureNameJob` — <purpose>

### 9. Mailers (if email needed)

- `FeatureNameMailer` — <purpose>

### 10. I18n

- View translations: `config/locales/views/{namespace}/{controller}.{locale}.yml`
- Model attributes: `config/locales/models/{model}.{locale}.yml`

### 11. Tests

- Model test: validations, associations, concern behavior
- Controller test: CRUD actions, authorization
- System test: user flow (if applicable)

## Implementation Order

1. [ ] Migration + Model (+ concerns)
2. [ ] Routes + Controller
3. [ ] Views + Turbo Frames/Streams
4. [ ] Helpers (display logic)
5. [ ] Stimulus (if needed)
6. [ ] Jobs / Mailers (if needed)
7. [ ] I18n translations
8. [ ] Tests

## Risks & Notes

- <Potential issues, edge cases, or things to watch out for>
- <Questions that need clarification from team>
```

### 4. Present the plan

After creating the file, display:
- The full plan to the user
- The file path: `${CLAUDE_PLUGIN_ROOT}/docs/plans/issue-<issue_id>.md`
- Ask if the plan looks good or needs adjustments

Tell the user:
```
Plan saved to ${CLAUDE_PLUGIN_ROOT}/docs/plans/issue-<issue_id>.md

When ready to implement, run:
  /implement <issue_id>

The implement command will automatically use this plan.
```

## Important Rules

- **DO NOT write any implementation code** — this is planning only
- **DO explore the codebase thoroughly** — the plan must be grounded in reality
- **DO check naming conventions** — all names in the plan must follow project standards
- **DO identify ALL affected namespaces** — a feature may span `/s`, `/c`, `/admin`, etc.
- **Display logic → helpers** — never plan display methods in models
- **No service classes** — always plan with concerns
- **RESTful routes only** — new screen = new controller

## References

- `${CLAUDE_PLUGIN_ROOT}/docs/ARCHITECTURE.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/NAMING_CONVENTIONS.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/CODE_OF_CONDUCT.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/HOTWIRE.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/ROUTES_POLICY.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/HELPERS.md`
