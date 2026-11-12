# designku

Design system catalog and enforcement for vibe-coded mobile apps, for Claude
Code and Codex. Platform-agnostic tokens; Flutter is the first generator
(React Native planned).

**Core rule: never assume a color, font, font size, spacing, radius, shadow or
theme. Use the project's design system; if the project has none, ask the user
to pick one with `/designku:ds-list`.**

## What's Included

- **6 commands** (`commands/`): `ds-list`, `ds-use`, `ds-apply`, `ds-show`, `ds-customize`, `ds-create`
- **3 skills** (`skills/`, shared with Codex): `design-system-rules` and `atomic-design` (reference — auto-invoked for Flutter UI work), `ds` (workflow entry point for Codex, `disable-model-invocation: true`)
- **1 agent**: `ds-reviewer` — audits token, atomic-level and accessibility violations
- **Hooks**: `PostToolUse` token enforcement on edited `.dart` files, `SessionStart` one-line reminder. Both are no-ops unless the project has `.designku/config.json`
- **9 built-in design systems** (`systems/<id>/`): `aegis` (fintech), `serene` (health), `bazaar` (e-commerce), `focus` (productivity), `sprout` (education/kids), `kopi` (F&B/lifestyle), `pulse` (social), `slate` (enterprise), `tinta` (creator tools, neo-brutalism) — each with `tokens.json`, `README.md` (rationale), `preview.html`
- **Scripts** (`scripts/`, python3 standard library only): one CLI `designku.py` (`list`, `show`, `use`, `apply`, `derive`, `validate`, `preview`, `fonts`)

## Storage

| What | Where |
| --- | --- |
| Built-in systems | `${CLAUDE_PLUGIN_ROOT}/systems/<id>/` |
| Custom systems (user level, shared by all projects) | `~/.designku/systems/<id>/` |
| Catalog page | `~/.designku/catalog.html` |
| Project selection | `<project>/.designku/config.json` |
| Project token snapshot (source of truth for generated code) | `<project>/.designku/tokens.json` |

## Standards

- Atomic design: tokens → atoms → molecules → organisms → templates → pages. A level only uses the levels below it. Pages compose templates/organisms and contain no styling.
- Outside the generated design system folder there are NO raw `Color(0x..)`, `Colors.*` (except `Colors.transparent`), hex strings, `TextStyle(fontSize: ..)`, `fontFamily:`, `GoogleFonts.*`, numeric `EdgeInsets` / gap `SizedBox` / `BorderRadius`, or hand-made `BoxShadow`.
- Tokens are read with `context.ds.colors.*`, `context.ds.text.*`, `DsSpacing` / `DsInsets`, `DsRadius` / `DsShape`, `DsElevation` / `DsShadows`, `DsEffect` (outline + hard shadow of brutal systems), `DsMotion`, `DsSizes` / `DsIconSize`.
- Use `Ds*` atoms (`DsButton`, `DsTextField`, `DsCard`, `DsStatusBadge`, `DsAvatar`, `DsGap`) instead of styling Material widgets in pages.
- Missing token or component → edit `.designku/tokens.json` and run `/designku:ds-apply`, or build the component at the right atomic level from tokens. Never hardcode, never edit generated files.
- Color pairs: content on `X` uses `onX`. Only those pairs are contrast-verified.
- Every system must pass `designku.py validate` (WCAG 2.2 AA: 4.5:1 text, 3:1 UI, light and dark). Do not bypass the validator.
- Status is never color alone (icon + label). Tap targets ≥ 48dp.
- In a UFIL modular project the generated code goes to `packages/presentation/feature_common/lib/src/design_system/`; UFIL's own rule says colors come from `AppColors` (`colors.xml`) — when both plugins are active, ask the user once which source owns UI colors instead of mixing them.

## Usage

```bash
# Local plugin directory
claude --plugin-dir /path/to/gm-aiagent-plugins/plugins/designku

# Or via marketplace
/plugin marketplace add ghozimahdi/gm-aiagent-plugins
/plugin install designku@gm-aiagent-plugins

# Browse, then pick / customize / create
/designku:ds-list

# Set the project default and generate Flutter code
/designku:ds-use aegis

# Edit .designku/tokens.json, then regenerate
/designku:ds-apply

# Custom systems (saved to ~/.designku/systems, reusable everywhere)
/designku:ds-customize slate
/designku:ds-create

# Current project system + preview link
/designku:ds-show
```

Codex: `$designku:ds list`, `$designku:ds use aegis`, `$designku:ds apply`, ...

## Maintaining the built-in catalog

Built-ins are generated, not hand-written: edit the spec/rationale in
`scripts/ds_builtins.py`, then run

```bash
python3 scripts/ds_builtins.py                  # rewrite systems/*/tokens.json + README.md
python3 scripts/designku.py validate            # must be 9/9 PASS
python3 scripts/designku.py preview --all       # re-render systems/*/preview.html
```

Bump `RENDERER_VERSION` in `scripts/ds_preview.py` when the preview layout
changes so existing previews are re-rendered. See `docs/TOKEN_SCHEMA.md` for
the token format.
