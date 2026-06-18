#!/bin/bash
# UserPromptSubmit hook shim — emits a one-line governance banner every turn (anti-drift).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)")"
exec python3 "$ROOT/automation/gatekeeper.py" status --terse
