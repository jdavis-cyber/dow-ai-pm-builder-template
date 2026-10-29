"""AI-1163: run records tell the truth (DEF-019, DEF-021, DEF-022).

- The result text names the status the dispatcher actually observed.
- An adapter can't label evidence Verified; only the Human Director's review can.
- An interrupted dispatch leaves a run result, or is recorded on the next run.
"""
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_commit_audit import ShellAdapterFixture  # noqa: E402

INDEX = "docs/verification/evidence-index.md"
CLOSE = ("p = pathlib.Path('orchestration/tasks.md')\n"
         "p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))\n")
EVIDENCE = "pathlib.Path('docs/verification/fixture.md').write_text('Synthetic verification only\\n')\n"


def append(path, line):
    return f"q = pathlib.Path({path!r}); q.write_text(q.read_text() + {line!r} + '\\n')\n"


class Records(ShellAdapterFixture):
    def records(self):
        runs = self.repo / "docs/verification/factory-runs"
        return [json.loads(p.read_text()) for p in sorted(runs.glob("*-result.json"))]


class StatusWordingTests(Records, unittest.TestCase):
    """DEF-019: 'changed status' was printed for a task whose status never changed."""

    def setUp(self):
        super().setUp()
        (self.repo / "docs/verification/fixture.md").write_text("old evidence\n")

    def test_unchanged_status_is_reported_as_unchanged(self):
        result, record = self.run_adapter("", complete=False)
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("changed status", result.stdout)
        self.assertIn("TASK-901 is still Ready and produced no new evidence", result.stdout)
        self.assertEqual(record["status_after_dispatch"], "Ready")
        self.assertEqual(record["checks"]["evidence_changed"], "fail: no evidence changed")

    def test_changed_status_names_the_new_status(self):
        result, record = self.run_adapter(CLOSE, complete=False)
        self.assertEqual(result.returncode, 3)
        self.assertIn("TASK-901 changed status to Done but produced no new evidence", result.stdout)
        self.assertEqual(record["status_after_dispatch"], "Done")


class VerifiedLabelTests(Records, unittest.TestCase):
    """DEF-021: an agent listed its own unreviewed artifacts as 'Verified task evidence'."""

    def test_adapter_marking_index_row_verified_is_flagged(self):
        row = "| EV-002 | 2026-10-29 | docs/verification/fixture.md | notes | review | abc123 | Verified task evidence |"
        result, record = self.run_adapter(append(INDEX, row))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("unreviewed evidence labelled verified", record["violations"])
        self.assertEqual(record["checks"]["verified_labels"]["added"], [{"path": INDEX, "line": row}])

    def test_adapter_marking_its_evidence_verified_is_flagged(self):
        body = EVIDENCE + append("docs/verification/fixture.md", "| Evidence Type | Verified |")
        result, record = self.run_adapter(body, complete=False)
        self.assertIn("unreviewed evidence labelled verified", record["violations"])
        self.assertEqual(record["checks"]["verified_labels"]["added"][0]["path"], "docs/verification/fixture.md")

    def test_generated_label_and_existing_human_verification_pass(self):
        human = "| EV-001 | 2026-10-01 | docs/a.md | notes | review | abc | Verified (Human Director review, GR-1) |"
        index = self.repo / INDEX
        index.write_text(index.read_text() + human + "\n")  # committed before the run
        row = "| EV-002 | 2026-10-29 | docs/verification/fixture.md | notes | pytest | abc | Generated — awaiting Human Director review |"
        result, record = self.run_adapter(append(INDEX, row) + append(INDEX, "Prose: results were unverified."))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["verified_labels"], "pass")


class InterruptionTests(Records, unittest.TestCase):
    """DEF-022: an operator stop mid-dispatch left a packet with no run result."""

    SLOW = ("import os, time\n"
            "pathlib.Path('started').write_text(str(os.getpid()))\n"
            "time.sleep(60)\n")

    def start(self, body):
        (self.repo / "adapter.py").write_text("import pathlib\n" + body)
        (self.repo / ".gitignore").write_text((self.repo / ".gitignore").read_text() + "\nstarted\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        command = shlex.join([sys.executable, "adapter.py"])
        proc = subprocess.Popen([sys.executable, "automation/governed_factory.py", "--adapter", "shell"],
                                cwd=self.repo, env={**self.env, "FACTORY_ADAPTER_COMMAND": command},
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        deadline = time.monotonic() + 30
        while not (self.repo / "started").exists():
            self.assertLess(time.monotonic(), deadline, "adapter never started")
            time.sleep(0.1)
        return proc, int((self.repo / "started").read_text())

    def assert_adapter_gone(self, pid):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)
        self.fail("the adapter outlived the interrupted factory")

    def assert_operator_stop_recorded(self, sig, name):
        proc, pid = self.start(self.SLOW)
        proc.send_signal(sig)
        out, _ = proc.communicate(timeout=30)
        self.assertEqual(proc.returncode, 128 + sig, out)
        self.assert_adapter_gone(pid)
        [record] = self.records()
        self.assertEqual(record["outcome"], f"interrupted: operator stop ({name}) during dispatch")
        self.assertIn("dispatch interrupted", record["violations"])
        self.assertRegex(record["task_packet"]["path"], r"-TASK-901\.json$")
        self.assertIn("write_audit", record["checks"])

    def test_ctrl_c_records_an_interrupted_result(self):
        self.assert_operator_stop_recorded(signal.SIGINT, "SIGINT")

    def test_sigterm_records_an_interrupted_result(self):
        self.assert_operator_stop_recorded(signal.SIGTERM, "SIGTERM")

    def test_killed_adapter_is_recorded_as_interrupted(self):
        result, record = self.run_adapter("import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n", complete=False)
        self.assertEqual(result.returncode, 128 + signal.SIGKILL, result.stdout + result.stderr)
        self.assertEqual(record["outcome"], "interrupted: adapter stopped by SIGKILL")
        self.assertIn("adapter interrupted", record["violations"])

    def test_killed_factory_leaves_a_marker_recorded_on_the_next_run(self):
        proc, pid = self.start(self.SLOW)
        proc.kill()
        proc.communicate(timeout=30)
        os.kill(pid, signal.SIGKILL)
        self.assertEqual(self.records(), [])
        packets = list((self.repo / "docs/verification/factory-runs").glob("*-TASK-901.json"))
        self.assertEqual(len(packets), 1)
        later = self.factory("shell")
        self.assertEqual(later.returncode, 3, later.stdout + later.stderr)
        self.assertIn("did not complete", later.stdout)
        [record] = self.records()
        self.assertTrue(record["outcome"].startswith("interrupted: dispatch did not complete"))
        self.assertEqual(record["task_packet"]["path"], str(packets[0].relative_to(self.repo)))
        # The interruption is recorded once; the next run carries on.
        again = self.factory("assisted")
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn("did not complete", again.stdout)


if __name__ == "__main__":
    unittest.main()
