---
description: "Review code for architecture violations and guideline compliance."
argument-hint: "[file, directory, or feature-name]"
allowed-tools: ["Read", "Glob", "Grep", "Bash"]
---

Review code for architecture violations and guideline compliance.

Arguments: $ARGUMENTS (file path, directory, or feature name)

## Step 0: Read docs

### 0a. Read plugin docs

Read from `${CLAUDE_PLUGIN_ROOT}/docs/` (resolve via `echo $CLAUDE_PLUGIN_ROOT`):
- `ARCHITECTURE.md`, `CODE_OF_CONDUCT.md`, `NAMING_CONVENTIONS.md`, `HOTWIRE.md`, `ROUTES_POLICY.md`

Also read the project's guidelines from `docs/guidelines/`:
- `CODE_OF_CONDUCT.md`, `NAMING_RULES.md`, `ROUTES_POLICY.md`, `HOTWIRE.md`, `ERROR_HANDLING.md`, `HELPERS.md`, `STIMULUS_CONTROLLERS.md`

## Checks

### Critical — Architecture Violations
- Business logic in controllers (must be in model concerns)
- Service classes (`app/services/`) — must use concerns
- Display logic in models/concerns — must use helpers (formatting, badges, status labels)
- Direct model queries (not through parent associations)
- Custom controller actions instead of RESTful resources
- `fetch()` in JavaScript for server communication
- `pushState`/`replaceState` in JavaScript
- `ENV` usage instead of Rails credentials
- Custom error rescue without justification
- `Rails.env` checks in application code

### Warning — Naming Violations
- Boolean columns with `is_`/`has_` prefix
- Datetime not ending in `_at`, date not ending in `_on`
- `def self.method` instead of `class << self`
- String comparison for enums instead of predicate methods
- Manual `.where(status: :x)` instead of enum scopes

### Warning — Frontend Violations
- Raw HTML forms instead of Rails form helpers
- `<button type="submit">` instead of `form.submit`
- Hardcoded URLs instead of URL helpers
- CSS `@import` for local files
- jQuery or vanilla JS
- Disabled Turbo without justification
- Cross-namespace helper usage

### Info — Code Quality
- Missing model validations
- Missing test coverage
- Non-English code comments
- Magic numbers for reference data
- Missing I18n (hardcoded text in views)
- Missing `AttributeLabels` include
- Missing `acts_as_paranoid` where needed

## Report Format

| File | Line | Issue | Severity | Guideline | Fix |
|------|------|-------|----------|-----------|-----|

Run `bundle exec rubocop` at the end to confirm zero style issues.

## References

- `${CLAUDE_PLUGIN_ROOT}/docs/ARCHITECTURE.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/CODE_OF_CONDUCT.md`
- `${CLAUDE_PLUGIN_ROOT}/docs/NAMING_CONVENTIONS.md`
