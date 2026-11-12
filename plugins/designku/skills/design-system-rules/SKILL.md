---
name: design-system-rules
description: "Hard rules for ANY Flutter UI work — building or editing a widget, page, screen, component, theme, color, font, text style, padding, spacing, radius, shadow or animation. Use design tokens and Ds* atoms only; never assume or hardcode colors, fonts, sizes or spacing. Load before writing or reviewing Dart UI code."
---

Resolve `DESIGNKU_ROOT` to the plugin root containing this skill. Claude Code
provides `CLAUDE_PLUGIN_ROOT`; Codex can resolve it from the installed skill
path (`<root>/skills/design-system-rules/SKILL.md`).

## Design System Rules (designku)

**You never choose a color, font, font size, spacing value, radius, shadow or
duration yourself.** Those decisions were made once, in the project's design
system. Your job is to apply them.

### Step 0 — Find the project's design system (before any UI code)

1. Read `.designku/config.json` at the project root:
   - `system` — the selected design system,
   - `output.dir` — where the generated code lives (default
     `lib/core/design_system/`; UFIL modular:
     `packages/presentation/feature_common/lib/src/design_system/`),
   - `tokens` — the token source (`.designku/tokens.json`).
2. **No config?** Stop and ask the user to choose one: run
   `/designku:ds-list` (Codex: `$designku:ds list`). Do not invent a theme
   "for now" and do not fall back to Material defaults or `Colors.blue`.
3. Skim the generated barrel (`design_system.dart`) and `atoms/` so you know
   what exists before writing anything new.

### The hierarchy

Tokens → Atoms → Molecules → Organisms → Templates → Pages. Each level uses
only the levels below it. See the `atomic-design` skill for what belongs where.

### Hard rules (outside the design system folder)

| Never write | Write instead |
| --- | --- |
| `Color(0xFF1A73E8)`, `Color.fromARGB(..)`, `Color.fromRGBO(..)` | `context.ds.colors.primary` (any semantic role) |
| `Colors.blue`, `Colors.grey[200]`, `Colors.white`, `Colors.black` | `context.ds.colors.surface`, `.onSurface`, `.outlineVariant`, ... (`Colors.transparent` is allowed) |
| `'#1A73E8'` hex strings | a semantic color role |
| `TextStyle(fontSize: 16, fontWeight: ..)` | `context.ds.text.bodyLarge` (+ `.copyWith(color: ...)` only) |
| `fontFamily: 'Inter'`, `GoogleFonts.inter()` | `context.ds.text.<role>`; mono → `DsTypography.mono(style)` |
| `EdgeInsets.all(16)`, `EdgeInsets.symmetric(horizontal: 12)` | `DsInsets.allLg`, `DsInsets.hMd`, `EdgeInsets.only(top: DsSpacing.sm)` |
| `SizedBox(height: 16)` as a gap | `const DsGap.lg()` |
| `BorderRadius.circular(8)`, `Radius.circular(12)` | `DsRadius.smAll`, `DsShape.card`, `DsShape.buttonBorder` |
| `BoxShadow(...)`, `elevation: 4` | `DsShadows.level2`, `DsElevation.level2` |
| `Duration(milliseconds: 300)` + `Curves.easeInOut` for UI motion | `DsMotion.slow`, `DsMotion.standardCurve` |
| `Icon(x, size: 20)` | `Icon(x, size: DsIconSize.sm)` |
| `ElevatedButton(...)`, `TextField(...)`, ad-hoc `Card` styling in pages | `DsButton`, `DsTextField`, `DsCard`, `DsStatusBadge`, `DsAvatar` |
| `ThemeData(...)`, `ColorScheme.fromSeed(...)` | `DsTheme.light` / `DsTheme.dark` (already wired) |

Accessing tokens:

```dart
import 'package:<app>/core/design_system/design_system.dart';

final ds = context.ds;
ds.colors.primary;        // semantic colors (light/dark aware)
ds.text.titleMedium;      // type scale
ds.spacing.md;            // == DsSpacing.md (use the static in const contexts)
ds.radius.lg;  ds.sizes.touchTarget;  ds.iconSize.md;
ds.motion.normal;  ds.motion.standardCurve;  ds.elevation.level1;
```

Color pairing is not optional: content on `primary` uses `onPrimary`, on
`primaryContainer` uses `onPrimaryContainer`, on any `surface*` uses
`onSurface` (primary text) or `onSurfaceVariant` (secondary text). These pairs
are the ones verified for WCAG contrast; other combinations are not.

### When something is missing

A needed color role, spacing step, size or component does not exist?
**Extend the system, do not hardcode:**

1. Token missing → add it to `.designku/tokens.json` (same DTCG shape as its
   neighbours; a new color goes into **both** `color.light` and `color.dark`,
   referencing a `color.palette.*` tone), then run `/designku:ds-apply`. The
   validator must pass. Schema: `${DESIGNKU_ROOT}/docs/TOKEN_SCHEMA.md`.
2. Component missing → build it at the right atomic level using tokens only
   (see `atomic-design`), in the app's shared widgets folder — not inline in
   a page, and not inside the generated folder.
3. Never edit generated files (`// GENERATED — do not edit.`); they are
   overwritten on the next apply.

If the user asks for a specific raw value ("make it #FF0000", "padding 13"),
say which token is closest and offer to add a token; only use
`// ds-ignore` on that line if they insist on a one-off.

### Accessibility (part of the system, not an extra)

- Tap targets ≥ 48 × 48 dp (`DsSizes.touchTarget`); `DsButton` and
  `IconButton` already comply — do not shrink them with `SizedBox`.
- Status is never color alone: use `DsStatusBadge` (icon + label) or add an
  icon and text yourself.
- Icon-only buttons need a `tooltip` / `semanticLabel`; images need
  `semanticLabel` or `excludeFromSemantics: true` when decorative.
- Respect system text scaling: no fixed heights around text, no
  `textScaler: TextScaler.noScaling`.
- Both themes must work: never branch on brightness to pick a literal color —
  semantic roles already switch.

### Enforcement

A PostToolUse hook (`scripts/ds_hook_check.py`) scans every edited `.dart`
file outside the design system folder and returns blocking feedback listing
the offending lines. Fix the lines with tokens; do not silence the hook with
`// ds-ignore` unless the user approved that exception. For a full audit use
the `ds-reviewer` agent.
