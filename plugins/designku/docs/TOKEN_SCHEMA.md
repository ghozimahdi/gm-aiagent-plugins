# Token Schema

Every designku design system is one file: `tokens.json`, in the
[W3C Design Tokens (DTCG)](https://www.designtokens.org/) format. It is the
single source of truth; previews and platform code are generated from it.

- A **token** is an object with `$value` and `$type` (optional `$description`).
- A **group** is any object without `$value`.
- An **alias** is a string `"{group.sub.token}"` that points at another token.
- Dimensions and durations use the object form `{"value": 16, "unit": "px"}` /
  `{"value": 200, "unit": "ms"}`.

```json
{
  "color": {
    "palette": { "primary": { "40": { "$type": "color", "$value": "#1F54D2" } } },
    "light":   { "primary": { "$type": "color", "$value": "{color.palette.primary.40}" } },
    "dark":    { "primary": { "$type": "color", "$value": "{color.palette.primary.80}" } }
  }
}
```

## Top-level groups

| Group | `$type` | Contents |
| --- | --- | --- |
| `$extensions.designku` | — | Identity and rationale: `id`, `name`, `letter`, `group`, `context`, `tagline`, `audience`, `personality[]`, `rationale{color,typography,shape,motion}`, `do[]`, `dont[]`, `fonts{display,body,mono}`, `base` (custom systems), `spec` (the generator input, see below), `schemaVersion` |
| `color.palette.<name>.<tone>` | `color` | **Primitives.** Tonal scales for `primary`, `secondary`, `tertiary`, `error`, `success`, `warning`, `info`, `neutral`, `neutralVariant`. Tone = CIE L\* (0 black … 100 white). UI code never uses these directly |
| `color.light.<role>` / `color.dark.<role>` | `color` | **Semantic roles** — aliases into the palette. Both modes must define the same roles |
| `typography.fontFamily.{display,body,mono}` | `fontFamily` | Family + fallbacks (array, first item is the Google Font) |
| `typography.scale.<role>` | `typography` | Material 3 roles: `display*`, `headline*`, `title*`, `body*`, `label*` (Large / Medium / Small). Composite: `fontFamily` (alias), `fontSize`, `fontWeight`, `lineHeight` (multiplier), `letterSpacing` |
| `spacing` | `dimension` | 4pt grid: `none` 0, `xxs` 2, `xs` 4, `sm` 8, `md` 12, `lg` 16, `xl` 24, `xxl` 32, `xxxl` 48, `huge` 64 |
| `radius` | `dimension` | `none`, `xs`, `sm`, `md`, `lg`, `xl`, `full` |
| `shape` | `dimension` | Per-component radius, aliases into `radius`: `button`, `input`, `card`, `chip`, `dialog`, `sheet` |
| `borderWidth` | `dimension` | `none`, `thin` 1, `thick` 2, `focus` 3 |
| `elevation.level0…level5` | `shadow` | Array of shadow layers (`color` as `#RRGGBBAA`, `offsetX`, `offsetY`, `blur`, `spread`); the Material dp value is in `$extensions.designku.dp` |
| `motion.duration` | `duration` | `instant`, `fast`, `normal`, `slow`, `slower` |
| `motion.easing` | `cubicBezier` | `standard`, `emphasized`, `decelerate`, `accelerate` |
| `iconSize` | `dimension` | `xs` 16, `sm` 20, `md` 24, `lg` 32, `xl` 48 |
| `size` | `dimension` | `touchTarget` (≥ 48), `buttonSm/Md/Lg`, `input`, `listItem`, `appBar`, `navBar`, `avatarSm/Md/Lg` |
| `opacity` | `number` | `disabled`, `disabledContainer`, `hover`, `focus`, `pressed`, `scrim` |

## Semantic color roles

For each family `primary`, `secondary`, `tertiary`, `error`, `success`,
`warning`, `info`:

| Role | Use | Default tone (light / dark) |
| --- | --- | --- |
| `<family>` | Filled components; also colored text/icons on surfaces | 40 / 80 |
| `on<Family>` | Content on `<family>` | 100 / 20 (auto-picked for contrast) |
| `<family>Container` | Low-emphasis fill | 90 / 30 |
| `on<Family>Container` | Content on the container | 10 / 90 |

Surfaces and lines (from `neutral` / `neutralVariant`): `background`,
`onBackground`, `surface`, `onSurface`, `surfaceDim`, `surfaceBright`,
`surfaceContainerLowest` … `surfaceContainerHighest`, `surfaceVariant`,
`onSurfaceVariant` (secondary text), `outline` (component boundaries, 3:1),
`outlineVariant` (decorative dividers), `inverseSurface`, `onInverseSurface`,
`inversePrimary`, `scrim`, `shadow`, `surfaceTint`.

Rule of use: content on `X` is always `onX`; on any `surface*` it is
`onSurface` or `onSurfaceVariant`.

## Why tones are CIE L\*

Palettes are generated in OKLCH (stable hue and chroma) but stepped by CIE L\*
lightness. WCAG contrast depends only on relative luminance, and L\* is a
function of luminance, so a fixed tone gap gives a guaranteed ratio for any
hue: a gap of 50 is at least 4.5:1, a gap of 40 at least 3:1. That is why the
default role mapping (40 on 98, 100 on 40, 10 on 90, 80 on 6, …) passes AA in
every system, and why changing the seed color cannot break contrast.

## Validation rules

`designku.py validate` fails a system when:

- a required role/token is missing, an alias does not resolve, or light and
  dark define different roles;
- any of the 67 checked pairs per mode is below its minimum — text 4.5:1
  (7:1 for `contrast: "AAA"`), UI components and large text 3:1;
- `error` is too close to `primary` (ΔE<sub>OK</sub> < 0.05, or < 0.10 with a
  hue gap under 30°);
- a spacing value is off the 4pt grid (`xxs` = 2 is the one exception),
  `size.touchTarget` / `size.input` / `size.listItem` is below 48, a font size
  is below 11px, `bodyMedium` is below 14px, or a body line height is
  below 1.3.

Warnings (not blocking): status colors that collapse under simulated
protanopia / deuteranopia / tritanopia (expected for equal-tone colors — hence
the icon + label rule), pure `#000000` dark surfaces, pure `#FFFFFF` dark-mode
text, fonts outside the curated list.

## Extending tokens in a project

Edit `<project>/.designku/tokens.json`, then run `/designku:ds-apply`.

Add a semantic color (for example a brand "premium" accent) — define it in
**both** modes, as aliases into an existing palette, together with its
on-color:

```json
"color": {
  "light": {
    "premium":   { "$type": "color", "$value": "{color.palette.tertiary.40}" },
    "onPremium": { "$type": "color", "$value": "{color.palette.tertiary.100}" }
  },
  "dark": {
    "premium":   { "$type": "color", "$value": "{color.palette.tertiary.80}" },
    "onPremium": { "$type": "color", "$value": "{color.palette.tertiary.20}" }
  }
}
```

After apply it is available as `context.ds.colors.premium`. Extra roles are
generated into `DsColors` automatically. Keep a tone gap of at least 50
between a text color and its background.

Add a spacing step or a component size the same way
(`"spacing": {"section": {"$type": "dimension", "$value": {"value": 40, "unit": "px"}}}`
→ `DsSpacing.section`). Token names must be camelCase identifiers.

## The generator spec

Built-in and custom systems are produced by `scripts/ds_engine.py` from a
compact spec, stored in `$extensions.designku.spec` so a system can be
re-derived (`/designku:ds-customize`):

| Key | Values | Effect |
| --- | --- | --- |
| `primary`, `secondary`, `tertiary` | hex / `null` | Palette seeds. `null` secondary/tertiary are derived from the primary and the mood |
| `error`, `success`, `warning`, `info` | hex | Status palette seeds |
| `neutralHue`, `neutralChroma` | degrees / 0–0.03 | Tint of greys (defaults to the primary hue) |
| `mood` | `calm`, `balanced`, `vibrant`, `professional`, `warm`, `playful` | Saturation of derived accents and neutrals |
| `fonts` | `{display, body, mono}` | Google Font families |
| `type` | weights + `displayTracking` | Weight per role group, optical tracking of display sizes |
| `corner` | `sharp`, `soft`, `rounded`, `pill` | `radius` scale and `shape` mapping |
| `density` | `compact`, `comfortable`, `spacious` | `size.*` (buttons 40 / 48 / 52, inputs 48 / 56 / 60, …) |
| `motion` | `snappy`, `balanced`, `expressive` | Duration multiplier (0.8 / 1 / 1.2) and emphasized curve |
| `elevation` | `flat`, `soft`, `lifted` | Shadow strength |
| `darkStyle` | `tinted`, `oled` | Dark surface tones (6 vs 4, never pure black) |
| `contrast` | `AA`, `AAA` | Role tone mapping and validator threshold |
| `tones` | `{light: {role: tone}, dark: {…}}` | Per-role tone overrides (e.g. Slate's graphite primary at tone 20) |

## Platform generators

`tokens.json` contains nothing platform-specific. A generator is one script
that reads it through the helpers in `scripts/dslib.py` (`tv`, `group_items`,
`alias_of`, `num`) and writes code:

- `scripts/ds_flutter.py` — Dart (`DsColors`, `DsTypography`, `DsTheme`, atoms)
- `scripts/ds_preview.py` — HTML/CSS preview
- planned: `scripts/ds_react_native.py`

`.designku/config.json` selects the generator with `"platform"`.
