#!/usr/bin/env bash
# SessionStart hook: if the project uses designku, remind the agent which
# design system is active. One line of output, nothing otherwise.
# Always exits 0 so it can never break a session.

set -u

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
while [[ -n "$dir" && "$dir" != "/" ]]; do
  if [[ -f "$dir/.designku/config.json" ]]; then
    python3 - "$dir/.designku/config.json" <<'PY' 2>/dev/null || true
import json, sys
try:
    c = json.load(open(sys.argv[1], encoding="utf-8"))
    s, o = c.get("system", {}), c.get("output", {})
    print(f"[designku] Active design system: {s.get('name')} ({s.get('id')}). UI code must use tokens/atoms from "
          f"{o.get('dir')} (context.ds.*, Ds* widgets) - never hardcode colors, fonts, spacing or radius. "
          f"Missing token? Edit .designku/tokens.json and run /designku:ds-apply.")
except Exception:
    pass
PY
    exit 0
  fi
  dir="$(dirname "$dir")"
done
exit 0
