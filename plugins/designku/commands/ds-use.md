---
description: "Set a design system as this project's default and generate the Flutter design system code from it."
argument-hint: "<id|letter> [--output <dir>] [--fonts google_fonts|asset]"
allowed-tools: ["Bash", "Read", "Edit", "AskUserQuestion"]
---

Pin a design system to the current project and apply it. Reply in the user's language.

1. If `$ARGUMENTS` has no system id, run `/designku:ds-list` instead and stop.
2. From the Flutter project root (the folder with `pubspec.yaml`; in a UFIL
   modular project that is the workspace root), run:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" use $ARGUMENTS
   ```

   This writes `.designku/config.json` (selected system, platform, output
   paths) and `.designku/tokens.json` (a project snapshot of the tokens — it
   must be committed), then generates the Dart code. Output goes to
   `lib/core/design_system/`, or to
   `packages/presentation/feature_common/lib/src/design_system/` (exported from
   `feature_common.dart`) when a UFIL modular project is detected.
3. Do every `ACTION:` line the script printed:
   - `flutter pub add google_fonts` in the stated package (skip if the user
     chose `--fonts asset`; then make sure the font families are declared in
     `pubspec.yaml`).
   - Wire the theme once in the app's `MaterialApp`:
     `theme: DsTheme.light, darkTheme: DsTheme.dark`. Read the existing
     `MaterialApp` first; if it already sets a hand-written theme, ask the
     user before replacing it.
4. Run `dart analyze` on the output folder and fix nothing by hand inside it —
   if analysis fails, report the error (generated files are never edited).
5. Report: system name, output folder, the preview link, and remind that from
   now on UI code must use `context.ds.*` and `Ds*` atoms (the
   `design-system-rules` skill and the post-edit hook enforce this).
