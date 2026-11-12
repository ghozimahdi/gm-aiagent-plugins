# designku

A Claude Code and Codex plugin that gives vibe-coded mobile apps a real design
system — so the AI agent **never assumes** a color, font, spacing, radius or
theme again.

designku ships a small catalog of curated, accessible design systems built on
**atomic design** (tokens → atoms → molecules → organisms → templates →
pages). You browse them as HTML previews, pick one as the project default,
customize one, or create your own; the plugin then generates the Flutter code
and enforces it on every edit.

## Why

Left alone, a coding agent invents a new blue, a new padding and a new font
size in every file. The result looks inconsistent, fails contrast checks and
cannot be re-themed. designku moves every visual decision into one
`tokens.json`, generates the platform code from it, and blocks edits that
bypass it.

- **One source of truth** — W3C DTCG `tokens.json`: tonal palettes → semantic
  roles (light + dark), type scale, 4pt spacing, radius, elevation, borders,
  motion, icon and component sizes.
- **Accessible by construction** — every text/background pair is validated
  against WCAG 2.2 AA (4.5:1 text, 3:1 UI) in both modes; a system that fails
  cannot be saved or applied.
- **Platform-agnostic** — tokens and the engine know nothing about Flutter.
  Flutter is the first generator; React Native is next.

## Install

### Claude Code

```bash
/plugin marketplace add ghozimahdi/gm-aiagent-plugins
/plugin install designku@gm-aiagent-plugins
```

### Codex

```bash
codex plugin marketplace add ghozimahdi/gm-aiagent-plugins
codex plugin add designku@gm-aiagent-plugins
```

Requires `python3` (3.9+, standard library only — no pip installs). Works on
its own or next to [`ufil`](../ufil/).

## Quick start

```bash
/designku:ds-list            # browse the catalog, then choose what to do
/designku:ds-use aegis       # or set a system directly (id or letter A–H)
```

Then build UI as usual. The agent now reads tokens from `context.ds.*` and
composes `Ds*` atoms; hardcoded values are rejected by the post-edit hook.

## Commands

| Command | What it does |
| --- | --- |
| `/designku:ds-list` | Lists built-in + custom systems with clickable `file://` preview links and the catalog page, then asks (arrow-key menu): set as project default, customize, create new, or just browse |
| `/designku:ds-use <id>` | Sets the project default and generates the code |
| `/designku:ds-apply` | Regenerates code from `.designku/tokens.json` (after you edit tokens). `--sync` re-pulls from the source system |
| `/designku:ds-show` | Prints the project's system, paths and preview link |
| `/designku:ds-customize <id>` | Interview (brand color, mood, fonts, corners, density) → new system derived from a base |
| `/designku:ds-create` | UX-research interview (industry, audience, personality, accessibility) → new system from scratch |

Codex has no plugin commands; use the shared workflow skill instead:
`$designku:ds list`, `$designku:ds use aegis`, `$designku:ds apply`,
`$designku:ds customize slate`, `$designku:ds create`.

Everything runs through one script, which you can also call directly:

```bash
python3 plugins/designku/scripts/designku.py list|show|use|apply|derive|validate|preview|fonts
```

## The catalog

Eight built-in systems, each with a distinct color identity and a researched
target context. Open any `systems/<id>/preview.html` in a browser, or read
`systems/<id>/README.md` for the full rationale (audience, personality, why
this palette and typography, do / don't).

| | ID | Name | Best for | Primary (light / dark) | Fonts (display / body) | Shape, density |
| --- | --- | --- | --- | --- | --- | --- |
| **A** | [`aegis`](systems/aegis/) | Aegis | Fintech, banking, insurance, payments | `#1F54D2` / `#AAC7FF` | Manrope / Public Sans | rounded, comfortable |
| **B** | [`serene`](systems/serene/) | Serene | Health, wellness, telemedicine, mental health, habits | `#166A5C` / `#88D5C3` | Outfit / Figtree | pill, spacious |
| **C** | [`bazaar`](systems/bazaar/) | Bazaar | E-commerce, marketplace, retail, deals | `#BA4400` / `#FFB599` | Plus Jakarta Sans | soft, comfortable |
| **D** | [`focus`](systems/focus/) | Focus | Productivity, tasks, notes, SaaS | `#4E44E3` / `#B9C3FF` | Inter | soft, compact |
| **E** | [`sprout`](systems/sprout/) | Sprout | Education, kids and family, gamified learning | `#216D00` / `#85DB6E` | Baloo 2 / Nunito | rounded, spacious |
| **F** | [`kopi`](systems/kopi/) | Kopi | Food and beverage, travel, lifestyle, hospitality | `#835332` / `#F2BB97` | Fraunces / DM Sans | soft, comfortable |
| **G** | [`pulse`](systems/pulse/) | Pulse | Social, community, creators, entertainment | `#B1008D` / `#FFADE3` | Sora / Be Vietnam Pro | pill, comfortable |
| **H** | [`slate`](systems/slate/) | Slate | Enterprise, B2B, admin, white-label base | `#29313D` / `#D9E3F3` | IBM Plex Sans | sharp, compact |

All fonts are free Google Fonts (OFL) with system fallbacks.

### What a preview shows

Each `preview.html` is a single self-contained file (inline CSS/JS; the only
network request is the Google Fonts stylesheet) rendered from `tokens.json`:

- **Overview** — audience, rationale, do / don't
- **Core tokens** — tonal palettes with hex, semantic colors with measured
  contrast, the full contrast audit table, type specimen, spacing, radius,
  elevation, borders, icon sizes, motion
- **Atoms** — buttons (all variants and states), text field, checkbox, radio,
  switch, chip, badge, status, avatar, icons, divider, progress
- **Molecules** — search bar, list tile, form field, card header, snackbar,
  banner, segmented control
- **Organisms** — app bar, bottom navigation, card, form, list section,
  dialog, empty state, bottom sheet
- **Templates** — auth, dashboard, list, detail, form, settings skeletons
- **Pages** in phone frames — login, register, home, list, detail, form,
  profile / settings

Light / dark toggle (or press `D`), sticky section navigation, responsive.

The catalog page `~/.designku/catalog.html` lists every system as a card;
use the **arrow keys** to move, **Enter** to open, `/` to filter.

## Where things are stored

| What | Where | Notes |
| --- | --- | --- |
| Built-in systems | `plugins/designku/systems/<id>/` | `tokens.json`, `README.md`, `preview.html` |
| **Your custom systems** | `~/.designku/systems/<id>/` | Same structure. User level, so they appear in `/designku:ds-list` in **every** project |
| Catalog page | `~/.designku/catalog.html` | Regenerated on every list |
| Project selection | `<project>/.designku/config.json` | System id + source, platform, output paths, enforcement settings |
| Project tokens | `<project>/.designku/tokens.json` | Snapshot of the selected system. Commit it — teammates and CI need neither the plugin nor `~/.designku` |

Set `DESIGNKU_HOME` to move the user-level folder.

## Generated Flutter code

`/designku:ds-apply` writes to `lib/core/design_system/` — or, in a UFIL
modular project (`packages/presentation/feature_common` exists), to
`packages/presentation/feature_common/lib/src/design_system/`, exported from
`feature_common.dart`. Change `output.dir` in `.designku/config.json` to put
it elsewhere.

| File | Contents |
| --- | --- |
| `ds_colors.dart` | `DsColors` `ThemeExtension` with every semantic role, `DsColors.light` / `.dark`, `toColorScheme()` |
| `ds_typography.dart` | `DsTypography.textTheme` (Material 3 roles) via `google_fonts`, or bundled fonts with `"flutter": {"fonts": "asset"}` |
| `ds_spacing.dart` | `DsSpacing`, `DsInsets` |
| `ds_radius.dart` | `DsRadius`, `DsShape` (per-component shapes) |
| `ds_elevation.dart` | `DsElevation` (dp), `DsShadows` |
| `ds_motion.dart` | `DsMotion` durations and curves |
| `ds_sizes.dart` | `DsSizes`, `DsIconSize`, `DsBorderWidth`, `DsOpacity` |
| `ds_theme.dart` | `DsTheme.light` / `.dark` — Material 3 `ThemeData` with component themes (buttons, inputs, cards, app bar, navigation bar, chips, dialogs, sheets, snackbars, list tiles, tabs) |
| `ds_context.dart` | `context.ds.colors.primary`, `context.ds.text.titleMedium`, `context.ds.spacing.md`, ... |
| `atoms/` | `DsButton`, `DsTextField`, `DsCard`, `DsStatusBadge`, `DsCountBadge`, `DsAvatar`, `DsGap` |
| `design_system.dart` | Barrel — the only import you need |

Every file starts with `// GENERATED — do not edit.` Change
`.designku/tokens.json` and re-run `/designku:ds-apply` instead. Requires
Flutter 3.27+ (Dart 3.6+).

```dart
MaterialApp(theme: DsTheme.light, darkTheme: DsTheme.dark);

final ds = context.ds;
Padding(
  padding: DsInsets.allLg,
  child: Text('Hello', style: ds.text.titleLarge?.copyWith(color: ds.colors.primary)),
);
```

## How enforcement works

| Layer | What it does |
| --- | --- |
| Skill `design-system-rules` | Auto-loaded for Flutter UI work. Hard rules: tokens and atoms only; if something is missing, extend `tokens.json` and regenerate — never hardcode |
| Skill `atomic-design` | What belongs at each level, with Flutter examples |
| Hook `PostToolUse` (`Write\|Edit\|MultiEdit\|apply_patch`) | Scans the edited `.dart` file (outside the design system folder) for `Color(0x..)`, `Colors.*`, hex strings, `TextStyle(fontSize:)`, `fontFamily:`, `GoogleFonts.*`, magic `EdgeInsets` / `SizedBox` gaps / `BorderRadius`, hand-made `BoxShadow`. Exits with code 2 and lists the offending lines plus the token to use, which Claude receives as blocking feedback |
| Hook `SessionStart` | One-line reminder of the active system (silent when the project has no config) |
| Agent `ds-reviewer` | Full audit: token violations, atomic-level violations, accessibility (contrast, 48dp targets, semantics) |

The hooks do nothing unless the project has `.designku/config.json`.

- For `Edit`, only the lines you changed are checked (`"enforce": {"scope":
  "changed"}`), so adopting designku in an existing codebase is not noisy. Set
  `"scope": "file"` to check whole files.
- Escape hatches: `// ds-ignore` on a line (or the line above),
  `// ds-ignore-file` anywhere in a file, glob patterns in `enforce.ignore`,
  or `"enforce": {"enabled": false}`.
- Manual scan: `python3 scripts/ds_hook_check.py --scan lib/**/*.dart`.

## Validation

```bash
python3 plugins/designku/scripts/designku.py validate        # every system
python3 plugins/designku/scripts/designku.py validate .designku/tokens.json -v
```

Checks 67 foreground/background pairs per mode against WCAG 2.2 (AA by
default, AAA when the system was created with `--contrast AAA`), required
tokens, alias resolution, the 4pt grid, minimum type sizes and line height,
48px touch targets, that `error` is distinguishable from `primary`, and
simulates protanopia / deuteranopia / tritanopia on the status colors.

## Docs

- [`docs/TOKEN_SCHEMA.md`](docs/TOKEN_SCHEMA.md) — token file format, how to
  extend it, the generator spec
- [`CLAUDE.md`](CLAUDE.md) — plugin overview for the agent

## Roadmap

- **React Native generator** (`ds_react_native.py`): the same `tokens.json` →
  TypeScript theme, `StyleSheet` tokens and base components; ESLint-based
  enforcement
- ScreenUtil-aware Flutter output for UFIL projects
- More atoms and generated molecules (search bar, list tile, form field)
- Figma variables export / import
- Jetpack Compose and SwiftUI generators

## License

[MIT](LICENSE)
