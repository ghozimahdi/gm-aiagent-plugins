# Design Systems (designku)

`designku` is the plugin that owns **visual decisions** — colors, typography,
spacing, radius, elevation, motion — for apps built with the plugins in this
repository. It is separate from the platform plugins on purpose: the same
design system must drive Flutter today and React Native next.

## How it fits with the other plugins

| Concern | Owner |
| --- | --- |
| Architecture, state management, project scaffolding (Flutter) | `ufil` |
| Design tokens, theme, atoms, UI enforcement | `designku` |

In a UFIL modular project designku generates into
`packages/presentation/feature_common/lib/src/design_system/` and exports it
from `feature_common.dart`; in a single-module project it generates into
`lib/core/design_system/`.

## The model

```
tokens.json (W3C DTCG, platform-agnostic)
   ├── preview.html        (per system, self-contained)
   ├── Flutter generator   → DsColors, DsTypography, DsTheme, Ds* atoms
   └── React Native generator (planned)
```

Atomic design levels: **tokens → atoms → molecules → organisms → templates →
pages**. A level only uses the levels below it.

## Storage conventions

| What | Where |
| --- | --- |
| Built-in systems | `plugins/designku/systems/<id>/` |
| User custom systems (shared by all projects) | `~/.designku/systems/<id>/` |
| Catalog page | `~/.designku/catalog.html` |
| Per-project selection | `<project>/.designku/config.json` |
| Per-project token snapshot (commit it) | `<project>/.designku/tokens.json` |

## Commands

`/designku:ds-list`, `/designku:ds-use <id>`, `/designku:ds-apply`,
`/designku:ds-show`, `/designku:ds-customize <id>`, `/designku:ds-create`.
In Codex: `$designku:ds <list|use|apply|show|customize|create>`.

## Enforcement hook

designku registers a `PostToolUse` hook on `Write|Edit|MultiEdit|apply_patch`.
It only acts when the project has `.designku/config.json`, scans the edited
`.dart` file for hardcoded colors, text styles and magic spacing, and exits
with code 2 (blocking feedback on stderr) when it finds any. Escape with
`// ds-ignore`.

## More

- Plugin README: [`plugins/designku/README.md`](https://github.com/ghozimahdi/gm-aiagent-plugins/blob/main/plugins/designku/README.md)
- Token schema: [`plugins/designku/docs/TOKEN_SCHEMA.md`](https://github.com/ghozimahdi/gm-aiagent-plugins/blob/main/plugins/designku/docs/TOKEN_SCHEMA.md)
