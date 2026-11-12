#!/usr/bin/env python3
"""designku Flutter generator: project tokens.json -> Dart design system.

Pure python3 stdlib. The token tree is platform-agnostic; this file is the only
place that knows about Flutter. A React Native generator would sit next to it
(ds_react_native.py) and read the same tokens.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import dslib as L
import ds_project
import ds_validate

HEADER = """// GENERATED — do not edit.
// Source: {tokens} ({name}).
// Edit the tokens and run /designku:ds-apply to regenerate.
"""

DART_RESERVED = {"default", "class", "new", "null", "true", "false", "in", "is", "do", "if", "for", "var", "final",
                 "const", "switch", "case", "this", "super", "void", "with", "enum", "else", "try", "return"}

COLOR_SCHEME_FIELDS = [
    "primary", "onPrimary", "primaryContainer", "onPrimaryContainer",
    "secondary", "onSecondary", "secondaryContainer", "onSecondaryContainer",
    "tertiary", "onTertiary", "tertiaryContainer", "onTertiaryContainer",
    "error", "onError", "errorContainer", "onErrorContainer",
    "surface", "onSurface", "surfaceDim", "surfaceBright", "surfaceContainerLowest", "surfaceContainerLow",
    "surfaceContainer", "surfaceContainerHigh", "surfaceContainerHighest", "onSurfaceVariant",
    "outline", "outlineVariant", "shadow", "scrim", "inverseSurface", "onInverseSurface", "inversePrimary", "surfaceTint",
]


def ident(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    out = parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    if not out or out[0].isdigit():
        out = "v" + out
    return out + "_" if out in DART_RESERVED else out


def cap(name: str) -> str:
    return name[:1].upper() + name[1:]


def dnum(value: float) -> str:
    return L.fmt_num(float(value))


def dcolor(hex_value: str) -> str:
    h = hex_value.lstrip("#").upper()
    if len(h) == 8:  # RRGGBBAA -> AARRGGBB
        return f"Color(0x{h[6:8]}{h[0:6]})"
    return f"Color(0xFF{h})"


def _items(tokens: dict, group: str) -> list[tuple[str, float]]:
    return [(ident(n), L.num(v)) for n, v in L.group_items(tokens, group)]


def _doubles(cls: str, doc: str, items: list[tuple[str, float]]) -> str:
    body = "\n".join(f"  static const double {n} = {dnum(v)};" for n, v in items)
    return f"/// {doc}\nabstract final class {cls} {{\n{body}\n}}\n"


def _accessor(cls: str, target: str, kind: str, names: list[str]) -> str:
    body = "\n".join(f"  {kind} get {n} => {target}.{n};" for n in names)
    return (f"/// Instance view of [{target}] for `context.ds`.\nclass {cls} {{\n  const {cls}();\n{body}\n}}\n")


# --------------------------------------------------------------------------- files


def gen_colors(tokens: dict) -> str:
    roles = [ident(n) for n, _ in L.group_items(tokens, "color.light")]
    fields = "\n".join(f"  final Color {r};" for r in roles)
    ctor = "\n".join(f"    required this.{r}," for r in roles)

    def instance(mode: str) -> str:
        values = "\n".join(f"    {ident(n)}: {dcolor(v)}," for n, v in L.group_items(tokens, f"color.{mode}"))
        return (f"  static const DsColors {mode} = DsColors(\n    brightness: Brightness.{mode},\n{values}\n  );")

    scheme = "\n".join(f"      {f}: {f}," for f in COLOR_SCHEME_FIELDS if f in roles)
    copy_params = "\n".join(f"    Color? {r}," for r in roles)
    copy_body = "\n".join(f"      {r}: {r} ?? this.{r}," for r in roles)
    lerp_body = "\n".join(f"      {r}: Color.lerp({r}, other.{r}, t)!," for r in roles)
    return f"""import 'package:flutter/material.dart';

/// Semantic colors of the design system (light and dark).
///
/// Read them with `context.ds.colors.primary`. Never use `Color(0x..)`,
/// `Colors.*` or hex strings in feature code.
@immutable
class DsColors extends ThemeExtension<DsColors> {{
  const DsColors({{
    required this.brightness,
{ctor}
  }});

  final Brightness brightness;
{fields}

{instance('light')}

{instance('dark')}

  /// Material [ColorScheme] built from the same roles.
  ColorScheme toColorScheme() {{
    return ColorScheme(
      brightness: brightness,
{scheme}
    );
  }}

  @override
  DsColors copyWith({{
    Brightness? brightness,
{copy_params}
  }}) {{
    return DsColors(
      brightness: brightness ?? this.brightness,
{copy_body}
    );
  }}

  @override
  DsColors lerp(ThemeExtension<DsColors>? other, double t) {{
    if (other is! DsColors) {{
      return this;
    }}
    return DsColors(
      brightness: t < 0.5 ? brightness : other.brightness,
{lerp_body}
    );
  }}
}}
"""


def gen_typography(tokens: dict, font_mode: str) -> str:
    fams = {slot: L.tv(tokens, f"typography.fontFamily.{slot}") for slot in ("display", "body", "mono")}

    def fallback(slot):
        return ", ".join(f"'{f}'" for f in fams[slot][1:])

    styles = []
    for role, style in L.group_items(tokens, "typography.scale"):
        raw = L.get_path(tokens, f"typography.scale.{role}")["$value"]["fontFamily"]
        slot = "display" if "display" in raw else ("mono" if "mono" in raw else "body")
        styles.append(f"    {ident(role)}: _style(\n      {slot}Family,\n      _{slot}Fallback,\n      {dnum(L.num(style['fontSize']))},\n"
                      f"      FontWeight.w{int(style['fontWeight'])},\n      {style['lineHeight']},\n      {dnum(L.num(style['letterSpacing']))},\n    ),")
    if font_mode == "google_fonts":
        imports = "import 'package:flutter/material.dart';\nimport 'package:google_fonts/google_fonts.dart';\n"
        build = """    return GoogleFonts.getFont(
      family,
      fontSize: size,
      fontWeight: weight,
      height: height,
      letterSpacing: spacing,
    ).copyWith(fontFamilyFallback: fallback);"""
        note = "Fonts are loaded with the `google_fonts` package."
    else:
        imports = "import 'package:flutter/material.dart';\n"
        build = """    return TextStyle(
      fontFamily: family,
      fontFamilyFallback: fallback,
      fontSize: size,
      fontWeight: weight,
      height: height,
      letterSpacing: spacing,
    );"""
        note = "Fonts are bundled assets: declare the families in pubspec.yaml."
    return f"""{imports}
/// Type scale of the design system (Material 3 roles).
///
/// {note}
/// Read styles with `context.ds.text.titleMedium`. Never write
/// `TextStyle(fontSize: ..)` or `fontFamily:` in feature code.
abstract final class DsTypography {{
  static const String displayFamily = '{fams['display'][0]}';
  static const String bodyFamily = '{fams['body'][0]}';
  static const String monoFamily = '{fams['mono'][0]}';

  static const List<String> _displayFallback = <String>[{fallback('display')}];
  static const List<String> _bodyFallback = <String>[{fallback('body')}];
  static const List<String> _monoFallback = <String>[{fallback('mono')}];

  static TextStyle _style(
    String family,
    List<String> fallback,
    double size,
    FontWeight weight,
    double height,
    double spacing,
  ) {{
{build}
  }}

  static final TextTheme textTheme = TextTheme(
{chr(10).join(styles)}
  );

  /// Monospace variant of [base] for codes, IDs and tabular numbers.
  static TextStyle mono(TextStyle base) {{
    return _style(
      monoFamily,
      _monoFallback,
      base.fontSize ?? 14,
      base.fontWeight ?? FontWeight.w400,
      base.height ?? 1.4,
      0,
    ).copyWith(color: base.color);
  }}
}}
"""


def gen_spacing(tokens: dict) -> str:
    items = _items(tokens, "spacing")
    insets = []
    for name, value in items:
        if value <= 0:
            continue
        insets.append(f"  static const EdgeInsets all{cap(name)} = EdgeInsets.all(DsSpacing.{name});")
        insets.append(f"  static const EdgeInsets h{cap(name)} = EdgeInsets.symmetric(\n    horizontal: DsSpacing.{name},\n  );")
        insets.append(f"  static const EdgeInsets v{cap(name)} = EdgeInsets.symmetric(\n    vertical: DsSpacing.{name},\n  );")
    return ("import 'package:flutter/widgets.dart';\n\n"
            + _doubles("DsSpacing", "Spacing scale (4pt grid). Use instead of numeric literals.", items)
            + "\n/// Ready-made paddings built from [DsSpacing].\nabstract final class DsInsets {\n"
            + "  static const EdgeInsets zero = EdgeInsets.zero;\n\n  /// Default screen padding.\n"
            + "  static const EdgeInsets screen = EdgeInsets.all(DsSpacing.lg);\n" + "\n".join(insets) + "\n}\n\n"
            + _accessor("DsSpacingTokens", "DsSpacing", "double", [n for n, _ in items]))


def gen_radius(tokens: dict) -> str:
    items = _items(tokens, "radius")
    all_ = "\n".join(f"  static const BorderRadius {n}All = BorderRadius.all(\n    Radius.circular({n}),\n  );" for n, _ in items)
    shapes, borders = [], []
    for name, _ in L.group_items(tokens, "shape"):
        alias = L.alias_of(tokens, f"shape.{name}")
        ref = f"DsRadius.{ident(alias.split('.')[-1])}" if alias and alias.startswith("radius.") else dnum(L.num(L.tv(tokens, f"shape.{name}")))
        shapes.append(f"  static const double {ident(name)}Radius = {ref};")
        shapes.append(f"  static const BorderRadius {ident(name)} = BorderRadius.all(\n    Radius.circular({ident(name)}Radius),\n  );")
        borders.append(f"  static const RoundedRectangleBorder {ident(name)}Border = RoundedRectangleBorder(\n    borderRadius: {ident(name)},\n  );")
    return ("import 'package:flutter/widgets.dart';\n\n"
            + f"/// Corner radius scale.\nabstract final class DsRadius {{\n"
            + "\n".join(f"  static const double {n} = {dnum(v)};" for n, v in items) + "\n\n" + all_ + "\n}\n\n"
            + "/// Component shapes (which radius each component uses).\nabstract final class DsShape {\n"
            + "\n".join(shapes) + "\n\n" + "\n".join(borders) + "\n\n"
            + "  /// Top-rounded shape for bottom sheets.\n  static const BorderRadius sheetTop = BorderRadius.vertical(\n    top: Radius.circular(sheetRadius),\n  );\n}\n\n"
            + _accessor("DsRadiusTokens", "DsRadius", "double", [n for n, _ in items]))


def gen_elevation(tokens: dict) -> str:
    dps, shadows = [], []
    for name, layers in L.group_items(tokens, "elevation"):
        dp = L.get_path(tokens, f"elevation.{name}").get("$extensions", {}).get("designku", {}).get("dp", 0)
        dps.append((ident(name), float(dp)))
        if not layers:
            shadows.append(f"  static const List<BoxShadow> {ident(name)} = <BoxShadow>[];")
            continue
        parts = "\n".join(
            f"    BoxShadow(\n      color: {dcolor(l['color'])},\n      offset: Offset({dnum(L.num(l['offsetX']))}, {dnum(L.num(l['offsetY']))}),\n"
            f"      blurRadius: {dnum(L.num(l['blur']))},\n      spreadRadius: {dnum(L.num(l['spread']))},\n    )," for l in layers)
        shadows.append(f"  static const List<BoxShadow> {ident(name)} = <BoxShadow>[\n{parts}\n  ];")
    return ("import 'package:flutter/widgets.dart';\n\n"
            + _doubles("DsElevation", "Material elevation (dp) per level.", dps)
            + "\n/// Box shadows per level, for custom-painted surfaces.\nabstract final class DsShadows {\n" + "\n".join(shadows) + "\n}\n\n"
            + _accessor("DsElevationTokens", "DsElevation", "double", [n for n, _ in dps]))


def gen_effects(tokens: dict) -> str:
    def val(name, default):
        try:
            return L.tv(tokens, f"effect.{name}")
        except KeyError:
            return default
    style = val("style", "material")
    stroke = L.num(val("strokeWidth", {"value": 0, "unit": "px"}))
    offset = L.num(val("shadowOffset", {"value": 0, "unit": "px"}))
    in_dark = bool(val("shadowInDark", False))
    return f"""import 'package:flutter/material.dart';

/// Surface style of this design system: `material` (soft shadows only) or
/// `brutal` (neo-brutalism: ink outline + hard offset shadow with zero blur).
///
/// Atoms read this; feature code never draws its own outline or shadow.
abstract final class DsEffect {{
  static const String style = '{style}';
  static const double strokeWidth = {dnum(stroke)};
  static const double shadowOffset = {dnum(offset)};
  static const bool shadowInDark = {'true' if in_dark else 'false'};

  static bool _active(BuildContext context) {{
    if (strokeWidth == 0 && shadowOffset == 0) {{
      return false;
    }}
    return shadowInDark || Theme.of(context).brightness == Brightness.light;
  }}

  /// Ink outline for primary actions and raised surfaces ([BorderSide.none]
  /// when the style has none or in dark mode without [shadowInDark]).
  static BorderSide stroke(BuildContext context) {{
    if (strokeWidth == 0 || !_active(context)) {{
      return BorderSide.none;
    }}
    return BorderSide(
      color: Theme.of(context).colorScheme.onSurface,
      width: strokeWidth,
    );
  }}

  /// Hard offset shadow (zero blur, onSurface color), empty when not used.
  static List<BoxShadow> hardShadow(BuildContext context) {{
    if (shadowOffset == 0 || !_active(context)) {{
      return const <BoxShadow>[];
    }}
    return <BoxShadow>[
      BoxShadow(
        color: Theme.of(context).colorScheme.onSurface,
        offset: const Offset(shadowOffset, shadowOffset),
      ),
    ];
  }}
}}
"""


def gen_motion(tokens: dict) -> str:
    durations = [(ident(n), int(L.num(v))) for n, v in L.group_items(tokens, "motion.duration")]
    easings = [(ident(n), v) for n, v in L.group_items(tokens, "motion.easing")]
    lines = [f"  static const Duration {n} = Duration(milliseconds: {v});" for n, v in durations]
    lines.append("")
    lines += [f"  static const Cubic {n}Curve = Cubic({', '.join(dnum(x) for x in v)});" for n, v in easings]
    acc = ("/// Instance view of [DsMotion] for `context.ds`.\nclass DsMotionTokens {\n  const DsMotionTokens();\n"
           + "\n".join(f"  Duration get {n} => DsMotion.{n};" for n, _ in durations) + "\n"
           + "\n".join(f"  Cubic get {n}Curve => DsMotion.{n}Curve;" for n, _ in easings) + "\n}\n")
    return ("import 'package:flutter/animation.dart';\n\n/// Motion durations and easing curves.\nabstract final class DsMotion {\n"
            + "\n".join(lines) + "\n}\n\n" + acc)


def gen_sizes(tokens: dict) -> str:
    size = _items(tokens, "size")
    opacity = [(ident(n), float(v)) for n, v in L.group_items(tokens, "opacity")]
    return (_doubles("DsSizes", "Component sizes. `touchTarget` is the minimum tap area.", size) + "\n"
            + _doubles("DsIconSize", "Icon sizes.", _items(tokens, "iconSize")) + "\n"
            + _doubles("DsBorderWidth", "Border widths.", _items(tokens, "borderWidth")) + "\n"
            + _doubles("DsOpacity", "State-layer and disabled opacities (0-1).", opacity) + "\n"
            + _accessor("DsSizeTokens", "DsSizes", "double", [n for n, _ in size]) + "\n"
            + _accessor("DsIconSizeTokens", "DsIconSize", "double", [n for n, _ in _items(tokens, "iconSize")]))


THEME = r"""import 'package:flutter/material.dart';

import 'ds_colors.dart';
import 'ds_elevation.dart';
import 'ds_radius.dart';
import 'ds_sizes.dart';
import 'ds_spacing.dart';
import 'ds_typography.dart';

/// Material 3 themes of the design system.
///
/// ```dart
/// MaterialApp(theme: DsTheme.light, darkTheme: DsTheme.dark);
/// ```
abstract final class DsTheme {
  static final ThemeData light = _build(DsColors.light);
  static final ThemeData dark = _build(DsColors.dark);

  static int _alpha(double opacity) => (opacity * 255).round();

  static ThemeData _build(DsColors c) {
    final ColorScheme scheme = c.toColorScheme();
    final TextTheme text = DsTypography.textTheme;
    final Color disabledFg = c.onSurface.withAlpha(_alpha(DsOpacity.disabled));
    final Color disabledBg = c.onSurface.withAlpha(
      _alpha(DsOpacity.disabledContainer),
    );

    OutlineInputBorder inputBorder(Color color, double width) {
      return OutlineInputBorder(
        borderRadius: DsShape.input,
        borderSide: BorderSide(color: color, width: width),
      );
    }

    const Size buttonSize = Size(DsSizes.touchTarget, DsSizes.buttonMd);
    const EdgeInsets buttonPadding = DsInsets.hXl;

    return ThemeData(
      useMaterial3: true,
      brightness: c.brightness,
      colorScheme: scheme,
      textTheme: text,
      scaffoldBackgroundColor: c.background,
      canvasColor: c.surface,
      dividerColor: c.outlineVariant,
      materialTapTargetSize: MaterialTapTargetSize.padded,
      extensions: <ThemeExtension<dynamic>>[c],
      appBarTheme: AppBarTheme(
        backgroundColor: c.surface,
        foregroundColor: c.onSurface,
        surfaceTintColor: Colors.transparent,
        elevation: DsElevation.level0,
        scrolledUnderElevation: DsElevation.level2,
        shadowColor: c.shadow,
        centerTitle: false,
        toolbarHeight: DsSizes.appBar,
        titleTextStyle: text.titleLarge?.copyWith(color: c.onSurface),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: buttonSize,
          padding: buttonPadding,
          shape: DsShape.buttonBorder,
          textStyle: text.labelLarge,
          disabledBackgroundColor: disabledBg,
          disabledForegroundColor: disabledFg,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: buttonSize,
          padding: buttonPadding,
          shape: DsShape.buttonBorder,
          textStyle: text.labelLarge,
          backgroundColor: c.surfaceContainerLow,
          foregroundColor: c.primary,
          elevation: DsElevation.level1,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: buttonSize,
          padding: buttonPadding,
          shape: DsShape.buttonBorder,
          textStyle: text.labelLarge,
          foregroundColor: c.primary,
          side: BorderSide(color: c.outline, width: DsBorderWidth.thin),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: buttonSize,
          padding: DsInsets.hMd,
          shape: DsShape.buttonBorder,
          textStyle: text.labelLarge,
          foregroundColor: c.primary,
        ),
      ),
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          minimumSize: const Size.square(DsSizes.touchTarget),
          iconSize: DsIconSize.md,
        ),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: c.primaryContainer,
        foregroundColor: c.onPrimaryContainer,
        elevation: DsElevation.level3,
        shape: const RoundedRectangleBorder(borderRadius: DsRadius.lgAll),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: c.surfaceContainerLowest,
        contentPadding: DsInsets.allLg,
        constraints: const BoxConstraints(minHeight: DsSizes.input),
        border: inputBorder(c.outline, DsBorderWidth.thin),
        enabledBorder: inputBorder(c.outline, DsBorderWidth.thin),
        focusedBorder: inputBorder(c.primary, DsBorderWidth.thick),
        errorBorder: inputBorder(c.error, DsBorderWidth.thick),
        focusedErrorBorder: inputBorder(c.error, DsBorderWidth.thick),
        disabledBorder: inputBorder(disabledBg, DsBorderWidth.thin),
        hintStyle: text.bodyLarge?.copyWith(color: c.onSurfaceVariant),
        labelStyle: text.bodyLarge?.copyWith(color: c.onSurfaceVariant),
        helperStyle: text.bodySmall?.copyWith(color: c.onSurfaceVariant),
        errorStyle: text.bodySmall?.copyWith(color: c.error),
        prefixIconColor: c.onSurfaceVariant,
        suffixIconColor: c.onSurfaceVariant,
      ),
      cardTheme: CardThemeData(
        color: c.surfaceContainerLow,
        surfaceTintColor: Colors.transparent,
        elevation: DsElevation.level0,
        margin: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(
          borderRadius: DsShape.card,
          side: BorderSide(
            color: c.outlineVariant,
            width: DsBorderWidth.thin,
          ),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        height: DsSizes.navBar,
        backgroundColor: c.surfaceContainer,
        surfaceTintColor: Colors.transparent,
        indicatorColor: c.secondaryContainer,
        elevation: DsElevation.level0,
        labelTextStyle: WidgetStateProperty.resolveWith<TextStyle?>((
          Set<WidgetState> states,
        ) {
          final bool selected = states.contains(WidgetState.selected);
          return text.labelMedium?.copyWith(
            color: selected ? c.onSurface : c.onSurfaceVariant,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith<IconThemeData?>((
          Set<WidgetState> states,
        ) {
          final bool selected = states.contains(WidgetState.selected);
          return IconThemeData(
            size: DsIconSize.md,
            color: selected ? c.onSecondaryContainer : c.onSurfaceVariant,
          );
        }),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        type: BottomNavigationBarType.fixed,
        backgroundColor: c.surfaceContainer,
        selectedItemColor: c.primary,
        unselectedItemColor: c.onSurfaceVariant,
        selectedLabelStyle: text.labelMedium,
        unselectedLabelStyle: text.labelMedium,
        elevation: DsElevation.level0,
      ),
      chipTheme: ChipThemeData(
        backgroundColor: c.surface,
        selectedColor: c.secondaryContainer,
        disabledColor: disabledBg,
        labelStyle: text.labelLarge?.copyWith(color: c.onSurfaceVariant),
        secondaryLabelStyle: text.labelLarge?.copyWith(
          color: c.onSecondaryContainer,
        ),
        padding: DsInsets.hSm,
        side: BorderSide(color: c.outline, width: DsBorderWidth.thin),
        shape: DsShape.chipBorder,
        showCheckmark: true,
        checkmarkColor: c.onSecondaryContainer,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: c.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
        elevation: DsElevation.level3,
        shape: DsShape.dialogBorder,
        titleTextStyle: text.headlineSmall?.copyWith(color: c.onSurface),
        contentTextStyle: text.bodyMedium?.copyWith(
          color: c.onSurfaceVariant,
        ),
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: c.surfaceContainerLow,
        surfaceTintColor: Colors.transparent,
        modalBarrierColor: c.scrim.withAlpha(_alpha(DsOpacity.scrim)),
        showDragHandle: true,
        dragHandleColor: c.outline,
        shape: const RoundedRectangleBorder(borderRadius: DsShape.sheetTop),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: c.inverseSurface,
        contentTextStyle: text.bodyMedium?.copyWith(
          color: c.onInverseSurface,
        ),
        actionTextColor: c.inversePrimary,
        elevation: DsElevation.level3,
        shape: const RoundedRectangleBorder(borderRadius: DsRadius.smAll),
      ),
      dividerTheme: DividerThemeData(
        color: c.outlineVariant,
        thickness: DsBorderWidth.thin,
        space: DsBorderWidth.thin,
      ),
      listTileTheme: ListTileThemeData(
        minTileHeight: DsSizes.listItem,
        contentPadding: DsInsets.hLg,
        iconColor: c.onSurfaceVariant,
        titleTextStyle: text.titleMedium?.copyWith(color: c.onSurface),
        subtitleTextStyle: text.bodyMedium?.copyWith(
          color: c.onSurfaceVariant,
        ),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: c.primary,
        linearTrackColor: c.surfaceContainerHighest,
        circularTrackColor: c.surfaceContainerHighest,
      ),
      tabBarTheme: TabBarThemeData(
        labelColor: c.primary,
        unselectedLabelColor: c.onSurfaceVariant,
        indicatorColor: c.primary,
        dividerColor: c.outlineVariant,
        labelStyle: text.titleSmall,
        unselectedLabelStyle: text.titleSmall,
      ),
    );
  }
}
"""

CONTEXT = r"""import 'package:flutter/material.dart';

import 'ds_colors.dart';
import 'ds_elevation.dart';
import 'ds_motion.dart';
import 'ds_radius.dart';
import 'ds_sizes.dart';
import 'ds_spacing.dart';

/// Entry point to every token: `context.ds.colors.primary`,
/// `context.ds.text.titleMedium`, `context.ds.spacing.md`, ...
class DsTokens {
  const DsTokens._(this._context);

  final BuildContext _context;

  DsColors get colors {
    final ThemeData theme = Theme.of(_context);
    return theme.extension<DsColors>() ??
        (theme.brightness == Brightness.dark ? DsColors.dark : DsColors.light);
  }

  TextTheme get text => Theme.of(_context).textTheme;
  DsSpacingTokens get spacing => const DsSpacingTokens();
  DsRadiusTokens get radius => const DsRadiusTokens();
  DsElevationTokens get elevation => const DsElevationTokens();
  DsMotionTokens get motion => const DsMotionTokens();
  DsSizeTokens get sizes => const DsSizeTokens();
  DsIconSizeTokens get iconSize => const DsIconSizeTokens();
}

extension DsContext on BuildContext {
  DsTokens get ds => DsTokens._(this);
}
"""

ATOMS = {
    "ds_gap.dart": r"""import 'package:flutter/widgets.dart';

import '../ds_spacing.dart';

/// Empty space between widgets in a Row or Column, sized by a spacing token.
///
/// Use instead of `SizedBox(height: 16)`.
class DsGap extends StatelessWidget {
  const DsGap(this.size, {super.key});

  const DsGap.xxs({super.key}) : size = DsSpacing.xxs;
  const DsGap.xs({super.key}) : size = DsSpacing.xs;
  const DsGap.sm({super.key}) : size = DsSpacing.sm;
  const DsGap.md({super.key}) : size = DsSpacing.md;
  const DsGap.lg({super.key}) : size = DsSpacing.lg;
  const DsGap.xl({super.key}) : size = DsSpacing.xl;
  const DsGap.xxl({super.key}) : size = DsSpacing.xxl;
  const DsGap.xxxl({super.key}) : size = DsSpacing.xxxl;

  /// One of the [DsSpacing] values.
  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(width: size, height: size);
  }
}
""",
    "ds_button.dart": r"""import 'package:flutter/material.dart';

import '../ds_context.dart';
import '../ds_effects.dart';
import '../ds_radius.dart';
import '../ds_sizes.dart';
import '../ds_spacing.dart';

enum DsButtonVariant { filled, tonal, outlined, text, danger }

enum DsButtonSize { sm, md, lg }

/// The only button feature code should use.
///
/// One [DsButtonVariant.filled] button per screen region; the tap area is
/// always at least [DsSizes.touchTarget].
class DsButton extends StatelessWidget {
  const DsButton({
    required this.label,
    required this.onPressed,
    this.variant = DsButtonVariant.filled,
    this.size = DsButtonSize.md,
    this.icon,
    this.loading = false,
    this.expand = false,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final DsButtonVariant variant;
  final DsButtonSize size;
  final IconData? icon;

  /// Shows a spinner and disables the button.
  final bool loading;

  /// Stretch to the full available width.
  final bool expand;

  double get _height => switch (size) {
    DsButtonSize.sm => DsSizes.buttonSm,
    DsButtonSize.md => DsSizes.buttonMd,
    DsButtonSize.lg => DsSizes.buttonLg,
  };

  @override
  Widget build(BuildContext context) {
    final colors = context.ds.colors;
    final VoidCallback? action = loading ? null : onPressed;
    // Brutal style: filled/danger actions get an ink outline + hard shadow.
    final bool raised =
        action != null &&
        (variant == DsButtonVariant.filled ||
            variant == DsButtonVariant.danger);
    final List<BoxShadow> shadows = raised
        ? DsEffect.hardShadow(context)
        : const <BoxShadow>[];
    final BorderSide stroke = raised
        ? DsEffect.stroke(context)
        : BorderSide.none;
    // A hard shadow must hug the visible button, so raised buttons are drawn
    // at least touchTarget tall instead of relying on invisible tap padding.
    final double height = shadows.isEmpty
        ? _height
        : (_height < DsSizes.touchTarget ? DsSizes.touchTarget : _height);
    ButtonStyle sizeStyle = ButtonStyle(
      minimumSize: WidgetStatePropertyAll<Size>(
        Size(expand ? double.infinity : DsSizes.touchTarget, height),
      ),
      tapTargetSize: MaterialTapTargetSize.padded,
    );
    if (stroke != BorderSide.none) {
      sizeStyle = sizeStyle.copyWith(
        side: WidgetStatePropertyAll<BorderSide>(stroke),
      );
    }

    final Widget child = Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        if (loading)
          const Padding(
            padding: EdgeInsets.only(right: DsSpacing.sm),
            child: SizedBox.square(
              dimension: DsIconSize.xs,
              child: CircularProgressIndicator(
                strokeWidth: DsBorderWidth.thick,
              ),
            ),
          )
        else if (icon != null)
          Padding(
            padding: const EdgeInsets.only(right: DsSpacing.sm),
            child: Icon(icon, size: DsIconSize.sm),
          ),
        Flexible(child: Text(label, overflow: TextOverflow.ellipsis)),
      ],
    );

    final Widget button = switch (variant) {
      DsButtonVariant.filled => FilledButton(
        onPressed: action,
        style: sizeStyle,
        child: child,
      ),
      DsButtonVariant.tonal => FilledButton.tonal(
        onPressed: action,
        style: sizeStyle,
        child: child,
      ),
      DsButtonVariant.outlined => OutlinedButton(
        onPressed: action,
        style: sizeStyle,
        child: child,
      ),
      DsButtonVariant.text => TextButton(
        onPressed: action,
        style: sizeStyle,
        child: child,
      ),
      DsButtonVariant.danger => FilledButton(
        onPressed: action,
        style: sizeStyle.copyWith(
          backgroundColor: WidgetStateProperty.resolveWith<Color?>((
            Set<WidgetState> states,
          ) {
            return states.contains(WidgetState.disabled) ? null : colors.error;
          }),
          foregroundColor: WidgetStateProperty.resolveWith<Color?>((
            Set<WidgetState> states,
          ) {
            return states.contains(WidgetState.disabled)
                ? null
                : colors.onError;
          }),
        ),
        child: child,
      ),
    };

    return Semantics(
      button: true,
      enabled: action != null,
      liveRegion: loading,
      child: shadows.isEmpty
          ? button
          : DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: DsShape.button,
                boxShadow: shadows,
              ),
              child: button,
            ),
    );
  }
}
""",
    "ds_text_field.dart": r"""import 'package:flutter/material.dart';

import '../ds_context.dart';
import '../ds_sizes.dart';
import '../ds_spacing.dart';

/// Text input with a persistent label above the field, helper and error text.
///
/// The label stays visible while typing (better for memory than a
/// placeholder-only field) and is merged into the field's semantics.
class DsTextField extends StatelessWidget {
  const DsTextField({
    required this.label,
    this.controller,
    this.hint,
    this.helper,
    this.error,
    this.prefixIcon,
    this.suffix,
    this.obscureText = false,
    this.enabled = true,
    this.maxLines = 1,
    this.keyboardType,
    this.textInputAction,
    this.onChanged,
    this.onSubmitted,
    super.key,
  });

  final String label;
  final TextEditingController? controller;
  final String? hint;
  final String? helper;

  /// When set, the field renders in the error state with this message.
  final String? error;
  final IconData? prefixIcon;
  final Widget? suffix;
  final bool obscureText;
  final bool enabled;
  final int maxLines;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    final bool hasError = error != null && error!.isNotEmpty;
    return MergeSemantics(
      child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Text(
          label,
          style: ds.text.labelLarge?.copyWith(
            color: hasError ? ds.colors.error : ds.colors.onSurface,
          ),
        ),
        const SizedBox(height: DsSpacing.xs),
        TextField(
          controller: controller,
          enabled: enabled,
          obscureText: obscureText,
          maxLines: obscureText ? 1 : maxLines,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
          style: ds.text.bodyLarge?.copyWith(color: ds.colors.onSurface),
          decoration: InputDecoration(
            hintText: hint,
            helperText: helper,
            errorText: hasError ? error : null,
            prefixIcon: prefixIcon == null
                ? null
                : Icon(prefixIcon, size: DsIconSize.sm),
            suffixIcon: suffix,
          ),
        ),
      ],
      ),
    );
  }
}
""",
    "ds_card.dart": r"""import 'package:flutter/material.dart';

import '../ds_context.dart';
import '../ds_effects.dart';
import '../ds_elevation.dart';
import '../ds_radius.dart';
import '../ds_sizes.dart';
import '../ds_spacing.dart';

enum DsCardVariant { outlined, elevated, filled }

/// Surface that groups related content. Tappable when [onTap] is set.
class DsCard extends StatelessWidget {
  const DsCard({
    required this.child,
    this.variant = DsCardVariant.outlined,
    this.padding = DsInsets.allLg,
    this.onTap,
    this.semanticLabel,
    super.key,
  });

  final Widget child;
  final DsCardVariant variant;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final colors = context.ds.colors;
    final (Color background, BorderSide side, double elevation) =
        switch (variant) {
          DsCardVariant.outlined => (
            colors.surfaceContainerLow,
            BorderSide(
              color: colors.outlineVariant,
              width: DsBorderWidth.thin,
            ),
            DsElevation.level0,
          ),
          DsCardVariant.elevated => (
            colors.surfaceContainerLowest,
            BorderSide.none,
            DsElevation.level1,
          ),
          DsCardVariant.filled => (
            colors.primaryContainer,
            BorderSide.none,
            DsElevation.level0,
          ),
        };
    final Widget content = Padding(padding: padding, child: child);
    final List<BoxShadow> hard = variant == DsCardVariant.elevated
        ? DsEffect.hardShadow(context)
        : const <BoxShadow>[];
    final Widget body = onTap == null
        ? content
        : InkWell(onTap: onTap, child: content);
    final Widget card = hard.isEmpty
        ? Card(
            color: background,
            elevation: elevation,
            shadowColor: colors.shadow,
            shape: RoundedRectangleBorder(
              borderRadius: DsShape.card,
              side: side,
            ),
            child: body,
          )
        : Padding(
            padding: const EdgeInsets.all(DsSpacing.xs),
            child: DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: DsShape.card,
                boxShadow: hard,
              ),
              child: Card(
                margin: EdgeInsets.zero,
                color: background,
                elevation: DsElevation.level0,
                shape: RoundedRectangleBorder(
                  borderRadius: DsShape.card,
                  side: DsEffect.stroke(context),
                ),
                child: body,
              ),
            ),
          );
    return Semantics(
      container: true,
      button: onTap != null,
      label: semanticLabel,
      child: card,
    );
  }
}
""",
    "ds_badge.dart": r"""import 'package:flutter/material.dart';

import '../ds_context.dart';
import '../ds_radius.dart';
import '../ds_sizes.dart';
import '../ds_spacing.dart';

enum DsStatus { success, warning, error, info, neutral }

/// Status pill. Always shows an icon and a label, so the meaning never
/// depends on color alone (color-blind safe).
class DsStatusBadge extends StatelessWidget {
  const DsStatusBadge({required this.status, required this.label, super.key});

  final DsStatus status;
  final String label;

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    final (Color background, Color foreground, IconData? icon) =
        switch (status) {
          DsStatus.success => (
            ds.colors.successContainer,
            ds.colors.onSuccessContainer,
            Icons.check_circle_outline,
          ),
          DsStatus.warning => (
            ds.colors.warningContainer,
            ds.colors.onWarningContainer,
            Icons.warning_amber_rounded,
          ),
          DsStatus.error => (
            ds.colors.errorContainer,
            ds.colors.onErrorContainer,
            Icons.error_outline,
          ),
          DsStatus.info => (
            ds.colors.infoContainer,
            ds.colors.onInfoContainer,
            Icons.info_outline,
          ),
          DsStatus.neutral => (
            ds.colors.surfaceContainerHighest,
            ds.colors.onSurfaceVariant,
            null,
          ),
        };
    return Semantics(
      label: '${status.name}: $label',
      excludeSemantics: true,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: background,
          borderRadius: DsRadius.fullAll,
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: DsSpacing.sm,
            vertical: DsSpacing.xs,
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              if (icon != null)
                Padding(
                  padding: const EdgeInsets.only(right: DsSpacing.xs),
                  child: Icon(icon, size: DsIconSize.xs, color: foreground),
                ),
              Text(
                label,
                style: ds.text.labelMedium?.copyWith(color: foreground),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Small count badge (notifications, cart).
class DsCountBadge extends StatelessWidget {
  const DsCountBadge({required this.count, this.max = 99, super.key});

  final int count;
  final int max;

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    final String text = count > max ? '$max+' : '$count';
    return Semantics(
      label: '$count',
      excludeSemantics: true,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: ds.colors.error,
          borderRadius: DsRadius.fullAll,
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: DsSpacing.xs + DsSpacing.xxs,
            vertical: DsSpacing.xxs,
          ),
          child: Text(
            text,
            style: ds.text.labelSmall?.copyWith(color: ds.colors.onError),
          ),
        ),
      ),
    );
  }
}
""",
    "ds_avatar.dart": r"""import 'package:flutter/material.dart';

import '../ds_context.dart';
import '../ds_sizes.dart';

enum DsAvatarSize { sm, md, lg }

/// Circular avatar: an image when [image] is set, otherwise initials.
class DsAvatar extends StatelessWidget {
  const DsAvatar({
    required this.name,
    this.image,
    this.size = DsAvatarSize.md,
    super.key,
  });

  /// Full name; used for the initials and the accessibility label.
  final String name;
  final ImageProvider? image;
  final DsAvatarSize size;

  String get _initials {
    final List<String> parts = name
        .trim()
        .split(RegExp(r'\s+'))
        .where((String p) => p.isNotEmpty)
        .toList();
    if (parts.isEmpty) {
      return '?';
    }
    final String first = parts.first.characters.first;
    final String last = parts.length > 1 ? parts.last.characters.first : '';
    return (first + last).toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    final (double diameter, TextStyle? style) = switch (size) {
      DsAvatarSize.sm => (DsSizes.avatarSm, ds.text.labelMedium),
      DsAvatarSize.md => (DsSizes.avatarMd, ds.text.titleSmall),
      DsAvatarSize.lg => (DsSizes.avatarLg, ds.text.titleLarge),
    };
    return Semantics(
      label: name,
      image: true,
      excludeSemantics: true,
      child: CircleAvatar(
        radius: diameter / 2,
        backgroundColor: ds.colors.primaryContainer,
        foregroundColor: ds.colors.onPrimaryContainer,
        backgroundImage: image,
        child: image == null
            ? Text(
                _initials,
                style: style?.copyWith(color: ds.colors.onPrimaryContainer),
              )
            : null,
      ),
    );
  }
}
""",
}


def gen_barrel(files: list[str], atoms: list[str]) -> str:
    lines = ["/// Design system barrel. Import this file only.", "library;", ""]
    lines += [f"export 'atoms/{a}';" for a in sorted(atoms)]
    lines += [f"export '{f}';" for f in sorted(files)]
    return "\n".join(lines) + "\n"


def _pubspec_has(pubspec: Path, package: str) -> bool:
    try:
        return bool(re.search(rf"^\s+{re.escape(package)}\s*:", pubspec.read_text(encoding="utf-8"), re.M))
    except OSError:
        return False


def apply(project: Path, sync: bool = False, fmt: bool = True) -> int:
    project = project.resolve()
    config = ds_project.load_config(project)
    if not config:
        print("error: no .designku/config.json here. Run /designku:ds-use <id> first (or /designku:ds-list to choose).")
        return 2
    if config.get("platform", "flutter") != "flutter":
        print(f"error: platform '{config.get('platform')}' has no generator yet (only flutter).")
        return 2
    tokens_path = project / config.get("tokens", ".designku/tokens.json")
    system_cfg = config.get("system", {})
    if sync:
        system = L.find_system(f"{system_cfg.get('source')}:{system_cfg.get('id')}")
        if not system:
            print(f"error: cannot sync — source system '{system_cfg.get('id')}' not found on this machine.")
            return 2
        text = Path(system["tokens_path"]).read_text(encoding="utf-8")
        tokens_path.write_text(text, encoding="utf-8")
        config["system"]["checksum"] = L.sha(text)
        L.write_json(ds_project.config_path(project), config)
        print(f"synced tokens from {system['source']}:{system['id']}")
    try:
        tokens = L.read_json(tokens_path)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read {tokens_path}: {exc}")
        return 2
    errors, warnings = ds_validate.validate(tokens)
    if errors:
        print(f"error: {tokens_path} fails validation — nothing generated:")
        for message in errors[:20]:
            print("  - " + message)
        return 1

    out_cfg = config.get("output") or ds_project.detect_layout(project)
    out_dir = project / out_cfg["dir"]
    font_mode = (config.get("flutter") or {}).get("fonts", "google_fonts")
    name = L.meta(tokens).get("name", system_cfg.get("id", "design system"))
    header = HEADER.format(tokens=config.get("tokens", ".designku/tokens.json"), name=name)

    files = {
        "ds_colors.dart": gen_colors(tokens),
        "ds_typography.dart": gen_typography(tokens, font_mode),
        "ds_spacing.dart": gen_spacing(tokens),
        "ds_radius.dart": gen_radius(tokens),
        "ds_elevation.dart": gen_elevation(tokens),
        "ds_motion.dart": gen_motion(tokens),
        "ds_effects.dart": gen_effects(tokens),
        "ds_sizes.dart": gen_sizes(tokens),
        "ds_theme.dart": THEME,
        "ds_context.dart": CONTEXT,
    }
    barrel = out_cfg.get("barrel", "design_system.dart")
    if out_dir.exists():  # drop stale generated files only (those carrying our header)
        for old in list(out_dir.glob("*.dart")) + list((out_dir / "atoms").glob("*.dart")):
            try:
                if old.read_text(encoding="utf-8").startswith("// GENERATED — do not edit."):
                    old.unlink()
            except OSError:
                pass
    (out_dir / "atoms").mkdir(parents=True, exist_ok=True)
    for filename, body in files.items():
        (out_dir / filename).write_text(header + "\n" + body, encoding="utf-8")
    for filename, body in ATOMS.items():
        (out_dir / "atoms" / filename).write_text(header + "\n" + body, encoding="utf-8")
    (out_dir / barrel).write_text(header + "\n" + gen_barrel(list(files), list(ATOMS)), encoding="utf-8")
    total = len(files) + len(ATOMS) + 1

    # UFIL modular: export the barrel from feature_common.dart
    export_from = out_cfg.get("exportFrom")
    if export_from:
        target = project / export_from
        try:
            rel = (out_dir / barrel).relative_to(target.parent).as_posix()
            line = f"export '{rel}';"
            current = target.read_text(encoding="utf-8") if target.is_file() else ""
            if line not in current:
                target.write_text(current.rstrip("\n") + ("\n" if current else "") + line + "\n", encoding="utf-8")
                print(f"exported from {export_from}")
        except (OSError, ValueError) as exc:
            print(f"warning: could not add export to {export_from}: {exc}")

    formatted = False
    if fmt and shutil.which("dart"):
        try:
            subprocess.run(["dart", "format", str(out_dir)], check=True, capture_output=True, timeout=120)
            formatted = True
        except (subprocess.SubprocessError, OSError):
            pass

    print(f"generated {total} files for {name} -> {out_dir}" + (" (dart format applied)" if formatted else ""))
    for message in warnings:
        print("warning: " + message)
    pubspec = project / out_cfg.get("pubspec", "pubspec.yaml")
    if font_mode == "google_fonts" and not _pubspec_has(pubspec, "google_fonts"):
        where = f" (in {pubspec.parent.relative_to(project)})" if pubspec.parent != project else ""
        print(f"ACTION: add the font package{where}: flutter pub add google_fonts")
    print("ACTION: wire the theme once — MaterialApp(theme: DsTheme.light, darkTheme: DsTheme.dark)")
    print(f"import:  {out_cfg['dir']}/{barrel}")
    return 0
