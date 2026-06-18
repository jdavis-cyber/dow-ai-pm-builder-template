#!/bin/bash
# SessionStart hook shim — refreshes Lock 0 and prints the governance re-injection banner.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)")"
python3 "$ROOT/automation/gatekeeper.py" refresh-lock0 >/dev/null 2>&1 || true
exec python3 "$ROOT/automation/gatekeeper.py" session-banner
