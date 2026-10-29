#!/usr/bin/env python3
"""Backward-compatible wrapper for the provider-neutral governed dispatcher.

Historically this file printed the next prompt only. It now delegates to
`automation/governed_factory.py` in assisted mode so existing operator commands
continue to work while the template uses the governed dispatcher contract.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    # Survive a console that is not UTF-8, e.g. cp1252 on Windows (AI-1151).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.dont_write_bytecode = True  # leave no __pycache__ behind in the project
    import safe_console
    safe_console.make_console_safe()
    raise SystemExit(
        subprocess.call(
            [sys.executable, str(ROOT / "automation" / "governed_factory.py"), "--adapter", "assisted"],
            cwd=ROOT,
        )
    )
