#!/usr/bin/env bash
# PostToolUse hook (Write|Edit|MultiEdit|apply_patch): design-token enforcement.
# Thin wrapper so the hook degrades to a no-op when python3 is unavailable.
# Exit code 2 + stderr = blocking feedback for the agent (Claude Code hook semantics).

set -u

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/ds_hook_check.py"
exit $?
