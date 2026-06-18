#!/bin/bash
# PreToolUse hook shim — delegates the decision to the shared gatekeeper brain.
# Usage (from a runtime hook config): pretooluse.sh <runtime>
# <runtime> is one of: claude | gemini | codex
# Reads the runtime's hook event JSON on stdin; emits allow/block on stdout.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)")"
exec python3 "$ROOT/automation/gatekeeper.py" hook --runtime "${1:?runtime arg required}"
