"""AI-1163: run records tell the truth (DEF-019, DEF-021, DEF-022).

- The result text names the status the dispatcher actually observed.
- An adapter can't label evidence Verified; only the Human Director's review can.
- An interrupted dispatch leaves a run result, or is recorded on the next run.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_commit_audit import ShellAdapterFixture  # noqa: E402
import governed_factory  # noqa: E402
from portable import portable_command  # noqa: E402

INDEX = "docs/verification/evidence-index.md"
CLOSE = ("p = pathlib.Path('orchestration/tasks.md')\n"
         "p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))\n")
EVIDENCE = "pathlib.Path('docs/verification/fixture.md').write_text('Synthetic verification only\\n')\n"


def append(path, line):
    return f"q = pathlib.Path({path!r}); q.write_text(q.read_text() + {line!r} + '\\n')\n"


class Records(ShellAdapterFixture):
    def records(self):
        runs = self.repo / "docs/verification/factory-runs"
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(runs.glob("*-result.json"))]


class StatusWordingTests(Records, unittest.TestCase):
    """DEF-019: 'changed status' was printed for a task whose status never changed."""

    def setUp(self):
        super().setUp()
        (self.repo / "docs/verification/fixture.md").write_text("old evidence\n", encoding="utf-8")

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
        index.write_text(index.read_text(encoding="utf-8") + human + "\n", encoding="utf-8")  # committed before the run
        row = "| EV-002 | 2026-10-29 | docs/verification/fixture.md | notes | pytest | abc | Generated — awaiting Human Director review |"
        result, record = self.run_adapter(append(INDEX, row) + append(INDEX, "Prose: results were unverified."))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["verified_labels"], "pass")


class VerifiedNoteTests(Records, unittest.TestCase):
    """Codex P2 on #29: only status declarations are human-only; factual notes pass."""

    def write_fixture(self, text):
        return f"pathlib.Path('docs/verification/fixture.md').write_text({text!r})\n"

    def test_factual_verified_notes_pass(self):
        # The shape directives/templates/verify.md suggests for an Evidence/Notes cell.
        text = ("| Acceptance Criterion | Result (Pass/Fail) | Evidence/Notes |\n"
                "| :--- | :--- | :--- |\n"
                "| AC 2: schema field | Pass | Verified field Z exists in schema |\n"
                "\nNotes: Verified the export opens in the viewer.\n")
        result, record = self.run_adapter(self.write_fixture(text))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["verified_labels"], "pass")

    def test_verified_in_a_status_column_is_flagged(self):
        text = "| Item | Gate Status |\n|---|---|\n| schema review | Verified |\n"
        result, record = self.run_adapter(self.write_fixture(text))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["verified_labels"]["added"],
                         [{"path": "docs/verification/fixture.md", "line": "| schema review | Verified |"}])

    def test_verified_status_field_line_is_flagged(self):
        result, record = self.run_adapter(self.write_fixture("Status: Verified\n"))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("unreviewed evidence labelled verified", record["violations"])


class InterruptionTests(Records, unittest.TestCase):
    """DEF-022: an operator stop mid-dispatch left a packet with no run result."""

    SLOW = ("import os, time\n"
            "pathlib.Path('started').write_text(str(os.getpid()))\n"
            "time.sleep(60)\n")

    def start(self, body):
        (self.repo / "adapter.py").write_text("import pathlib\n" + body, encoding="utf-8")
        (self.repo / ".gitignore").write_text((self.repo / ".gitignore").read_text(encoding="utf-8") + "\nstarted\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        command = portable_command(sys.executable, "adapter.py")
        proc = subprocess.Popen([sys.executable, "automation/governed_factory.py", "--adapter", "shell"],
                                cwd=self.repo, env={**self.env, "FACTORY_ADAPTER_COMMAND": command},
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        deadline = time.monotonic() + 30
        while not (self.repo / "started").exists():
            self.assertLess(time.monotonic(), deadline, "adapter never started")
            time.sleep(0.1)
        return proc, int((self.repo / "started").read_text(encoding="utf-8"))

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

    def test_marker_left_after_its_result_was_recorded_is_consumed(self):
        # Codex P2 on #29: a stop between write_run_result() and the marker delete
        # left a marker for a dispatch already recorded; recovery appended a second,
        # false "interrupted" result for the same dispatch.
        result, record = self.run_adapter("")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        anchor = Path(self.env["FACTORY_CHAIN_ANCHOR_DIR"])
        in_flight = anchor / hashlib.sha256(str(self.repo.resolve()).encode()).hexdigest()[:24] / "in-flight"
        self.assertTrue(in_flight.parent.is_dir())
        in_flight.mkdir(exist_ok=True)
        marker = in_flight / (Path(record["task_packet"]["path"]).stem + ".json")
        marker.write_text(json.dumps({
            "task_id": "TASK-901", "dispatched_at_utc": record.get("dispatched_at_utc"), "adapter": "shell",
            "task_packet": record["task_packet"],
            "owner": {"pid": 1, "host": socket.gethostname(), "token": "crashed", "started_at_utc": None}}), encoding="utf-8")
        later = self.factory("shell")
        self.assertNotIn("did not complete", later.stdout)
        self.assertEqual(later.returncode, 0, later.stdout + later.stderr)
        self.assertEqual(len(self.records()), 1)
        self.assertFalse(marker.exists())

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
        self.assertEqual(record["task_packet"]["path"], packets[0].relative_to(self.repo).as_posix())
        # The interruption is recorded once; the next run carries on.
        again = self.factory("assisted")
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn("did not complete", again.stdout)

    def test_recovery_refuses_while_the_interrupted_adapter_still_runs(self):
        # Codex P2 on #29: a killed factory frees the lock, but its adapter lives on in
        # its own process group; recovery must not dispatch the task a second time.
        proc, pid = self.start(self.SLOW)
        try:
            proc.kill()
            proc.communicate(timeout=30)
            [marker] = self.in_flight_markers()
            identity = json.loads(marker.read_text(encoding="utf-8"))["adapter_process"]
            self.assertEqual(identity["pgid"], os.getpgid(pid))
            for adapter in ("shell", "assisted"):
                with self.subTest(adapter=adapter):
                    later = self.factory(adapter)
                    self.assertEqual(later.returncode, 75, later.stdout + later.stderr)
                    self.assertIn("adapter from interrupted dispatch still running", later.stdout)
                    self.assertEqual(self.records(), [])
                    self.assertEqual(self.in_flight_markers(), [marker])
        finally:
            os.kill(pid, signal.SIGKILL)
        self.assert_adapter_gone(pid)
        # Once the adapter has exited, recovery records the interruption as before.
        later = self.factory("shell")
        self.assertEqual(later.returncode, 3, later.stdout + later.stderr)
        [record] = self.records()
        self.assertTrue(record["outcome"].startswith("interrupted: dispatch did not complete"))
        self.assertEqual(record["adapter_process"], identity)
        self.assertEqual(self.in_flight_markers(), [])

    def in_flight_markers(self):
        return list(Path(self.env["FACTORY_CHAIN_ANCHOR_DIR"]).rglob("in-flight/*.json"))

    def test_second_invocation_during_a_live_dispatch_is_refused(self):
        # Codex P2 on #29: a concurrent run read the live marker as a crash.
        proc, pid = self.start(self.SLOW)
        try:
            for adapter in ("shell", "assisted"):
                with self.subTest(adapter=adapter):
                    second = self.factory(adapter)
                    self.assertEqual(second.returncode, 75, second.stdout + second.stderr)
                    self.assertIn("dispatch in progress", second.stdout)
                    self.assertEqual(self.records(), [])
                    self.assertEqual(len(self.in_flight_markers()), 1)
            marker = json.loads(self.in_flight_markers()[0].read_text(encoding="utf-8"))
            self.assertEqual(marker["owner"]["pid"], proc.pid)
            self.assertTrue(marker["owner"]["host"] and marker["owner"]["token"])
        finally:
            proc.send_signal(signal.SIGINT)
            proc.communicate(timeout=30)
        self.assert_adapter_gone(pid)
        [record] = self.records()
        self.assertTrue(record["outcome"].startswith("interrupted: operator stop"))
        self.assertEqual(self.in_flight_markers(), [])

    def test_marker_from_another_host_is_not_recovered(self):
        (self.repo / "adapter.py").write_text("", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        anchor = Path(self.env["FACTORY_CHAIN_ANCHOR_DIR"])
        self.assertEqual(self.factory("assisted").returncode, 0)  # creates the operator-side folders
        in_flight = next(anchor.rglob("pending")).parent / "in-flight"
        in_flight.mkdir(exist_ok=True)
        marker = in_flight / "20261029T000000Z-TASK-901.json"
        marker.write_text(json.dumps({"task_id": "TASK-901", "owner": {
            "pid": 1, "host": "some-other-host.invalid", "token": "abc", "started_at_utc": None}}), encoding="utf-8")
        result = self.factory("assisted")
        self.assertEqual(result.returncode, 75, result.stdout + result.stderr)
        self.assertIn("some-other-host.invalid", result.stdout)
        self.assertTrue(marker.exists())
        self.assertEqual(self.records(), [])


class AdapterIdentityTests(unittest.TestCase):
    """Recovery tells a surviving adapter from an exited one or a reused pid."""

    def spawn(self):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        self.addCleanup(lambda: (proc.kill(), proc.wait()))
        return proc

    def test_running_adapter_is_still_running(self):
        proc = self.spawn()
        identity = governed_factory.adapter_identity(proc)
        self.assertEqual(identity["pgid"], None if os.name == "nt" else proc.pid)
        self.assertTrue(governed_factory.adapter_still_running(identity))

    def test_exited_adapter_is_not_running(self):
        proc = self.spawn()
        identity = governed_factory.adapter_identity(proc)
        proc.kill()
        proc.wait()
        self.assertFalse(governed_factory.adapter_still_running(identity))

    def test_reused_pid_is_not_the_recorded_adapter(self):
        proc = self.spawn()
        identity = governed_factory.adapter_identity(proc)
        self.assertIsNotNone(identity["start_time"])
        self.assertFalse(governed_factory.adapter_still_running({**identity, "start_time": "another process"}))

    def test_malformed_identity_is_not_running(self):
        for identity in ({}, {"pid": "1"}, {"pid": True}, {"pid": 0}):
            with self.subTest(identity=identity):
                self.assertFalse(governed_factory.adapter_still_running(identity))

    def test_windows_checks_the_adapter_process_and_its_start_time(self):
        with mock.patch.object(governed_factory, "_on_windows", return_value=True), \
                mock.patch.object(governed_factory, "_windows_process", return_value=(True, 1234)) as probe:
            self.assertTrue(governed_factory.adapter_still_running({"pid": 42, "pgid": None, "start_time": 1234}))
            self.assertFalse(governed_factory.adapter_still_running({"pid": 42, "pgid": None, "start_time": 99}))
            probe.return_value = (False, 1234)
            self.assertFalse(governed_factory.adapter_still_running({"pid": 42, "pgid": None, "start_time": 1234}))
        probe.assert_called_with(42)


if __name__ == "__main__":
    unittest.main()
