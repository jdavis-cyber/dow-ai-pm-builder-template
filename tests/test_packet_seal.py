"""AI-1154: an adapter can't rewrite the task packet it was dispatched with.

The packet records what the factory sent and under which authority. It sits in
the agent-writable evidence folder, so its digest is taken before the adapter
starts, kept in the chained run result, and checked after the run and on every
later chain verification.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_commit_audit import ShellAdapterFixture  # noqa: E402
import gatekeeper  # noqa: E402
import governed_factory  # noqa: E402

REWRITE_PACKET = (
    "import json, os\n"
    "pp = pathlib.Path(os.environ['FACTORY_TASK_PACKET'])\n"
    "pk = json.loads(pp.read_text()); pk['gate_state']['implementation_authorized'] = True\n"
    "pp.write_text(json.dumps(pk, indent=2))\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PacketAuthorityTests(unittest.TestCase):
    def test_packet_carries_every_authority_flag(self):
        for value in (True, False):
            state = {flag: value for flag in gatekeeper.AUTHORITY_FLAGS}
            gate = governed_factory.build_packet({"Task ID": "TASK-1"}, state)["gate_state"]
            self.assertEqual({flag: gate.get(flag) for flag in gatekeeper.AUTHORITY_FLAGS}, state)
        self.assertEqual(len(gatekeeper.AUTHORITY_FLAGS), 8)

    def test_packets_written_in_the_same_second_do_not_overwrite(self):
        import tempfile
        saved = governed_factory.ROOT, governed_factory.LOG_DIR
        with tempfile.TemporaryDirectory() as td:
            governed_factory.ROOT = Path(td)
            governed_factory.LOG_DIR = Path(td) / "runs"
            try:
                first, second = {}, {}
                packet = {"task": {"Task ID": "TASK-1"}}
                governed_factory.write_packet(packet, first)
                governed_factory.write_packet(packet, second)
                self.assertNotEqual(first["task_packet"]["path"], second["task_packet"]["path"])
                self.assertEqual(governed_factory.packet_seal_problem(first["task_packet"]), "")
            finally:
                governed_factory.ROOT, governed_factory.LOG_DIR = saved


class PacketSealTests(ShellAdapterFixture, unittest.TestCase):
    def packet(self, record):
        return self.repo / record["task_packet"]["path"]

    def test_untouched_packet_is_sealed_in_the_result(self):
        result, record = self.run_adapter("")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["task_packet"], "pass")
        self.assertEqual(record["task_packet"]["sha256"], sha(self.packet(record)))

    def test_adapter_rewriting_its_packet_fails_the_run(self):
        result, record = self.run_adapter(REWRITE_PACKET)
        self.assert_violation(result, record, "task packet modified")
        self.assertTrue(record["checks"]["task_packet"].startswith("fail"))
        self.assertNotEqual(record["task_packet"]["sha256"], sha(self.packet(record)))
        self.assertIn("task packet", result.stdout)
        # The rewrite is already a chained violation; it does not wedge later runs.
        later = self.factory("assisted")
        self.assertNotIn("evidence trail broken", later.stdout + later.stderr)

    def test_adapter_deleting_its_packet_fails_the_run(self):
        result, record = self.run_adapter("import os; os.remove(os.environ['FACTORY_TASK_PACKET'])\n")
        self.assert_violation(result, record, "task packet modified")

    def test_later_packet_edit_breaks_the_evidence_trail(self):
        result, record = self.run_adapter("")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packet = self.packet(record)
        packet.write_text(packet.read_text().replace('"implementation_authorized": false',
                                                     '"implementation_authorized": true'))
        later = self.factory("assisted")
        self.assertEqual(later.returncode, 2, later.stdout + later.stderr)
        self.assertIn("evidence trail broken", later.stdout)
        self.assertIn(packet.name, later.stdout)

    def test_assisted_packet_edited_before_completion_is_flagged(self):
        (self.repo / "adapter.py").write_text("")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        first = self.factory("assisted")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        baseline = json.loads((self.repo / "docs/verification/factory-runs/pending-assisted/TASK-901.json").read_text())
        packet = self.repo / baseline["task_packet"]["path"]
        packet.write_text(packet.read_text().replace('"implementation_authorized": false',
                                                     '"implementation_authorized": true'))
        (self.repo / "docs/verification/fixture.md").write_text("Synthetic verification only\n")
        board = self.repo / "orchestration/tasks.md"
        board.write_text(board.read_text().replace("**Status**: Ready", "**Status**: Done"))
        done = self.factory("assisted")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        records = list((self.repo / "docs/verification/factory-runs").glob("*-result.json"))
        self.assertEqual(len(records), 1)
        self.assertIn("task packet modified", json.loads(records[0].read_text())["violations"])


if __name__ == "__main__":
    unittest.main()
