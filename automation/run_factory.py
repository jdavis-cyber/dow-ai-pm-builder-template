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
    raise SystemExit(
        subprocess.call(
            [sys.executable, str(ROOT / "automation" / "governed_factory.py"), "--adapter", "assisted"],
            cwd=ROOT,
        )
    )
