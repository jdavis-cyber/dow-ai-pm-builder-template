#!/bin/bash
# Thin wrapper for shell users — the canonical, cross-platform implementation
# is init_project.py (works on macOS, Linux, and Windows).
exec python3 "$(dirname "$0")/init_project.py" "$@"
