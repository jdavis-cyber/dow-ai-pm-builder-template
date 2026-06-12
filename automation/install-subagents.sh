#!/usr/bin/env bash
# Thin wrapper for shell users — the canonical, cross-platform implementation
# is install_subagents.py (works on macOS, Linux, and Windows).
exec python3 "$(dirname "$0")/install_subagents.py" "$@"
