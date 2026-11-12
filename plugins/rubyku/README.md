# Rubyku — Rails Plugin for Claude Code

A Claude Code plugin for **Rails 8** development that enforces Rails Way architecture and a Hotwire-first frontend.

## Features

### 3 Agents

| Agent | Model | Role |
|-------|-------|------|
| **rubyku-architect** | Opus | Plans features, designs architecture, creates implementation tasks |
| **rubyku-implementer** | Sonnet | Writes production code following Rails Way standards |
| **rubyku-reviewer** | Sonnet | Audits code for guideline violations, reports findings |

### 13 Commands

| Command | Description |
|---------|-------------|
| `/plan` | Analyze an issue and write a detailed implementation plan before coding |
| `/implement` | Implement a feature end-to-end (architect → implement → verify) |
| `/implement-batch` | Implement multiple features in parallel with auto-scaled agents |
| `/commit` | Git commit with `[#issue_id] Message` format |
| `/create-pr` | Create GitHub PR with structured description |
| `/check` | Run RuboCop + Brakeman before committing |
| `/test` | Run Minitest suite and report results |
| `/fix-tests` | Run tests and automatically fix failures |
| `/review` | Audit code for architecture violations |
| `/ship` | Full pipeline: test → review → commit → PR |
| `/generate-migration` | Generate migration with naming conventions |
| `/github-issue` | Create a GitHub issue in the current repo |
| `/resolve-conflicts` | Resolve git merge conflicts intelligently |

### 8 Skills

| Skill | Description |
|-------|-------------|
| **rails-way** | Thin controllers, fat models, concerns, Rails conventions |
| **hotwire** | Turbo Frames → Turbo Streams → Stimulus priority |
| **turbo** | Turbo Frames and Streams patterns |
| **stimulus** | Stimulus controller patterns and namespace rules |
| **testing** | Minitest patterns: model, controller, job, system tests |
| **naming-conventions** | Database columns, models, controllers, git workflow |
| **concerns-pattern** | Business logic organization with concerns (no services) |
| **ai-agents** | AI Agent architecture for workflow automation |

### Hooks

- **Pre-commit**: Auto-run RuboCop on staged `.rb` files
- **Post-edit**: Guideline reviewer checks compliance on Write/Edit

## Requirements

- Ruby on Rails 8 project
- `bundle`, `bin/rails` available in PATH
- `gh` CLI authenticated (for issue/PR commands)

## Installation

Install via the marketplace or point to the plugin directly:

```bash
# Add to .claude/settings.json in your Rails project:
{
  "plugins": ["rubyku"]
}

# Or use as a plugin directory:
claude --plugin-dir /path/to/rubyku
```

## Quick Start

```bash
# Plan a feature from a GitHub issue
/plan 123

# Implement it
/implement 123

# Or skip planning and implement directly
/implement "add user notifications"

# Run checks
/check

# Run tests
/test

# Commit
/commit

# Ship everything
/ship
```

## Architecture Overview

```
Controllers (thin) → Models (fat) → Concerns (business logic)
     │                    │
     ├── Strong params    ├── Validations
     ├── Query via assoc  ├── Callbacks
     └── Render/redirect  ├── Scopes
                          └── Enum predicates

Frontend: Turbo Frames → Turbo Streams → Stimulus
Background: Solid Queue → Jobs → Mailers
```

## License

MIT
