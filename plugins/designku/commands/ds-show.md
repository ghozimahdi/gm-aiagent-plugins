---
description: "Show which design system this project uses, where its tokens and generated code live, and the preview link."
argument-hint: ""
allowed-tools: ["Bash"]
model: haiku
---

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/designku.py" show
```

Relay the output as-is (keep the `file://` preview link on its own line so it
is clickable). If no design system is selected, suggest `/designku:ds-list`.
If the output has a `note:` about drift, explain it in one sentence.
