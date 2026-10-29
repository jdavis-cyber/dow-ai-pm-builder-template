"""AI-1151: entry points still run on a console that isn't UTF-8 (cp1252 on Windows)."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import safe_console  # noqa: E402

ENTRY_POINTS = sorted(p.name for p in (ROOT / "automation").glob("*.py")
                      if p.name != "safe_console.py" and "__main__" in p.read_text(encoding="utf-8"))


class LegacyConsoleTests(unittest.TestCase):
    def legacy_env(self):
        return {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}

    def test_init_project_runs_on_a_cp1252_console(self):
        with tempfile.TemporaryDirectory() as parent:
            result = subprocess.run([sys.executable, "automation/init_project.py", "cp1252-project", parent],
                                    cwd=ROOT, env=self.legacy_env(), capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout.decode("cp1252", "replace")
                         + result.stderr.decode("cp1252", "replace"))
        self.assertIn(b"Instantiating project", result.stdout)

    def test_every_entry_point_makes_its_console_safe(self):
        self.assertIn("init_project.py", ENTRY_POINTS)
        for name in ENTRY_POINTS:
            with self.subTest(entry_point=name):
                text = (ROOT / "automation" / name).read_text(encoding="utf-8")
                self.assertTrue("safe_console.make_console_safe()" in text, f"{name} does not call it")

    def test_only_streams_that_are_not_utf8_are_changed(self):
        import io
        legacy = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        utf8 = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        safe_console.make_console_safe(legacy, utf8)
        self.assertEqual(legacy.errors, "replace")
        self.assertEqual(utf8.errors, "strict")
        legacy.write("▶ ok")
        legacy.flush()
        self.assertEqual(legacy.buffer.getvalue(), b"? ok")


if __name__ == "__main__":
    unittest.main()
