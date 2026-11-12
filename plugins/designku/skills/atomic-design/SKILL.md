---
name: atomic-design
description: "Atomic design for Flutter UI — what belongs at each level (tokens, atoms, molecules, organisms, templates, pages) with examples. Use when creating, placing, splitting or reviewing widgets, components, screens or pages, or deciding where a new piece of UI should live."
---

Resolve `DESIGNKU_ROOT` to the plugin root containing this skill (Claude Code:
`CLAUDE_PLUGIN_ROOT`; Codex: derive it from the installed skill path).

## Atomic Design in Flutter (designku)

A page is never built from raw widgets and literals. It is assembled from
smaller, named, reusable levels. Open the project's design system preview
(`/designku:ds-show` prints the link) to see every level rendered.

| Level | What it is | May use | Must not | Lives in |
| --- | --- | --- | --- | --- |
| **0 Tokens** | Named decisions: color roles, type scale, spacing, radius, elevation, motion, sizes | — | be edited by hand (generated) | `<output.dir>/ds_*.dart` |
| **1 Atoms** | One indivisible control with all its states: button, text field, checkbox, chip, badge, avatar, icon, divider, gap, progress | tokens | know about business data, navigate, call blocs | generated: `<output.dir>/atoms/`; your own: `widgets/atoms/` |
| **2 Molecules** | A few atoms doing one job: search bar, list tile, labelled form field, card header, snackbar content, segmented control | atoms, tokens | fetch data, hold feature state | `widgets/molecules/` |
| **3 Organisms** | A self-contained region: app bar, bottom nav, product/item card, form, list section, dialog, empty state | molecules, atoms, tokens | decide page layout, call use cases | `widgets/organisms/` (feature-specific ones inside the feature) |
| **4 Templates** | Page skeleton with slots — where organisms go, scrolling, safe areas, sticky bars | organisms (as parameters) | contain real content or state | `widgets/templates/` |
| **5 Pages** | A template filled with real data and wired to state management | templates, organisms | style anything directly | `features/<feature>/presentation/pages/` |

`widgets/` means the project's shared presentation folder (single module:
`lib/core/widgets/` or `lib/common/widgets/`; UFIL modular:
`packages/presentation/feature_common/lib/src/widgets/`). Follow the folder
the project already uses.

### Deciding the level

- Could it appear in a totally different app unchanged, and it is one control? → **atom**.
- Is it 2–4 atoms that always travel together? → **molecule**.
- Does it have a recognisable purpose on its own ("the order summary")? → **organism**.
- Is it only arrangement (slots, padding, scroll)? → **template**.
- Does it know a route, a bloc or an entity? → **page** (or a feature-level organism).

Reuse first: search atoms/molecules before creating. Create a new component
when the same structure appears a second time — not a third.

### Examples

Atom — tokens only, every state handled, accessible by default:

```dart
class DsTag extends StatelessWidget {
  const DsTag({required this.label, super.key});
  final String label;

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: ds.colors.secondaryContainer,
        borderRadius: DsShape.chip,
      ),
      child: Padding(
        padding: DsInsets.hSm,
        child: Text(
          label,
          style: ds.text.labelMedium?.copyWith(
            color: ds.colors.onSecondaryContainer,
          ),
        ),
      ),
    );
  }
}
```

Molecule — atoms composed for one job, data passed in as plain values:

```dart
class UserTile extends StatelessWidget {
  const UserTile({required this.name, required this.subtitle, this.onTap, super.key});
  final String name;
  final String subtitle;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final ds = context.ds;
    return ListTile(
      onTap: onTap,
      leading: DsAvatar(name: name),
      title: Text(name),          // styled by the theme (listTileTheme)
      subtitle: Text(subtitle),
      trailing: Icon(Icons.chevron_right, size: ds.iconSize.sm),
    );
  }
}
```

Organism — a region; receives data and callbacks, owns no navigation:

```dart
class LoginForm extends StatelessWidget {
  const LoginForm({required this.onSubmit, this.emailError, this.loading = false, super.key});
  final VoidCallback onSubmit;
  final String? emailError;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: <Widget>[
        DsTextField(label: 'Email', error: emailError, keyboardType: TextInputType.emailAddress),
        const DsGap.lg(),
        const DsTextField(label: 'Password', obscureText: true),
        const DsGap.xl(),
        DsButton(label: 'Log in', onPressed: onSubmit, loading: loading, expand: true),
      ],
    );
  }
}
```

Template — layout and slots only:

```dart
class AuthTemplate extends StatelessWidget {
  const AuthTemplate({required this.title, required this.form, this.footer, super.key});
  final String title;
  final Widget form;
  final Widget? footer;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: DsInsets.screen,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              const DsGap.xxl(),
              Text(title, style: context.ds.text.headlineMedium),
              const DsGap.xl(),
              form,
              const Spacer(),
              if (footer != null) footer!,
            ],
          ),
        ),
      ),
    );
  }
}
```

Page — fills the template, wires state; contains **no** styling:

```dart
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<LoginBloc, LoginState>(
      builder: (context, state) => AuthTemplate(
        title: 'Welcome back',
        form: LoginForm(
          loading: state.isLoading,
          emailError: state.emailError,
          onSubmit: () => context.read<LoginBloc>().add(const LoginEvent.submitted()),
        ),
      ),
    );
  }
}
```

### Level violations to avoid

- A page with `Container`/`Padding`/`TextStyle` styling → extract an organism or use a template.
- An atom that takes a domain model (`OrderModel`) → pass plain values (`String title`).
- A molecule that calls a bloc, repository or navigator → lift it; pass a callback.
- A template with hardcoded strings or an `if (user.isPremium)` → that belongs in the page.
- Duplicating an existing atom with slightly different padding → add a variant/size to the atom.
- Skipping levels downward is fine (a page may use an atom); reaching upward is not (an atom must never import an organism).

Token rules for all levels are in the `design-system-rules` skill.
