"""Regression tests for governed-factory P1 governance fixes.

Guards two Codex P1 findings on the provider-neutral governed factory:

  P1-1 (gatekeeper.check_action): an authorized implementation/source write
        (implementation_authorized == True) must be ALLOWED, not fail closed.
  P1-2 (governed_factory.task_needs_human): tasks using the documented
        task-schema Gate Impact values ("advances gate" / "blocks gate")
        must trigger a human gate stop.
"""

import os
import pathlib
import sys
import unittest

AUTOMATION = pathlib.Path(__file__).resolve().parents[1] / "automation"
sys.path.insert(0, str(AUTOMATION))

import gatekeeper  # noqa: E402
import governed_factory  # noqa: E402


class GatekeeperAuthorizedWriteTests(unittest.TestCase):
    def test_authorized_source_write_is_allowed(self):
        for prefix in gatekeeper.PROTECTED_SOURCE_PREFIXES:
            ok, msg = gatekeeper.check_action(
                "write", prefix + "thing", {"implementation_authorized": True}
            )
            self.assertTrue(ok, f"{prefix}: {msg}")

    def test_unauthorized_source_write_still_blocked(self):
        ok, _ = gatekeeper.check_action(
            "write", "src/app.py", {"implementation_authorized": False}
        )
        self.assertFalse(ok)

    def test_planning_write_allowed(self):
        ok, _ = gatekeeper.check_action("write", "docs/x.md", {})
        self.assertTrue(ok)

    def test_unknown_path_write_fails_closed_even_when_authorized(self):
        ok, _ = gatekeeper.check_action(
            "write", "random/x", {"implementation_authorized": True}
        )
        self.assertFalse(ok)


class TaskNeedsHumanGateTests(unittest.TestCase):
    def test_documented_gate_values_stop(self):
        self.assertTrue(governed_factory.task_needs_human({"Gate Impact": "advances gate"}))
        self.assertTrue(governed_factory.task_needs_human({"Gate Impact": "blocks gate"}))

    def test_phrasal_gate_impact_stops(self):
        self.assertTrue(
            governed_factory.task_needs_human(
                {"Gate Impact": "blocks Gate 1 until compliance review exists"}
            )
        )

    def test_non_gate_impact_does_not_stop(self):
        self.assertFalse(governed_factory.task_needs_human({"Gate Impact": "none"}))

    def test_planning_only_override_preserved(self):
        self.assertFalse(
            governed_factory.task_needs_human(
                {"Gate Impact": "advances gate", "Status": "planning only"}
            )
        )


class PostDispatchDetectiveControlTests(unittest.TestCase):
    """The dispatcher's governance claim depends on observing the adapter
    AFTER dispatch, not just gating selection before it. These tests pin the
    fail-closed detective behavior so a refactor cannot silently return the
    factory to advisory-only governance."""

    def test_unauthorized_protected_write_detected(self):
        viol = governed_factory.unauthorized_writes(
            set(), {"src/app.py", "docs/notes.md"}, {"implementation_authorized": False}
        )
        self.assertEqual(viol, ["src/app.py"])

    def test_authorized_write_not_flagged(self):
        viol = governed_factory.unauthorized_writes(
            set(), {"src/app.py"}, {"implementation_authorized": True}
        )
        self.assertEqual(viol, [])

    def test_preexisting_dirt_not_attributed_to_adapter(self):
        viol = governed_factory.unauthorized_writes(
            {"src/app.py"}, {"src/app.py"}, {"implementation_authorized": False}
        )
        self.assertEqual(viol, [])

    def test_missing_evidence_reported(self):
        task = {"Task ID": "TASK-999", "Evidence Required": "`docs/verification/TASK-999/verify.md`"}
        self.assertEqual(
            governed_factory.missing_evidence(task),
            ["docs/verification/TASK-999/verify.md"],
        )

    def test_existing_evidence_passes(self):
        task = {"Task ID": "TASK-000", "Evidence Required": "`README.md` and `automation/gatekeeper.py`"}
        self.assertEqual(governed_factory.missing_evidence(task), [])

    def test_non_path_backticks_ignored(self):
        task = {"Task ID": "TASK-000", "Evidence Required": "`approved` marker in gate record"}
        self.assertEqual(governed_factory.evidence_paths(task), [])


    def test_run_result_is_persisted(self):
        import json, tempfile, pathlib as pl
        orig = governed_factory.LOG_DIR
        try:
            with tempfile.TemporaryDirectory() as td:
                governed_factory.LOG_DIR = pl.Path(td)
                task = {"Task ID": "TASK-TEST"}
                path = governed_factory.write_run_result(task, {"record_type": "factory-run-result", "outcome": "pass"})
                data = json.loads(path.read_text())
                self.assertEqual(data["outcome"], "pass")
                self.assertTrue(path.name.endswith("TASK-TEST-result.json"))
        finally:
            governed_factory.LOG_DIR = orig


class AuthorityStoreTests(unittest.TestCase):
    """JER-39: the agent cannot grant itself authority."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / "project"
        (self.root / ".governance").mkdir(parents=True)
        self.key = pathlib.Path(self.tmp.name) / "operator.key"
        self.key.write_text("k" * 64 + "\n")
        self._saved = (gatekeeper.ROOT, gatekeeper.GATE_STATE)
        gatekeeper.ROOT = self.root
        gatekeeper.GATE_STATE = self.root / ".governance" / "gate_state.json"
        self._env = os.environ.get(gatekeeper.OPERATOR_KEY_ENV)
        os.environ[gatekeeper.OPERATOR_KEY_ENV] = str(self.key)

    def tearDown(self):
        gatekeeper.ROOT, gatekeeper.GATE_STATE = self._saved
        if self._env is None:
            os.environ.pop(gatekeeper.OPERATOR_KEY_ENV, None)
        else:
            os.environ[gatekeeper.OPERATOR_KEY_ENV] = self._env
        self.tmp.cleanup()

    def _approved(self):
        return {"approval_state": "approved", "decision": "Gate 1 approved", "implementation_authorized": True}

    def test_authority_record_write_denied_even_when_authorized(self):
        for path in [".governance/gate_state.json", ".governance/security-compliance/override-register.md"]:
            ok, msg = gatekeeper.check_action("write", path, {"implementation_authorized": True})
            self.assertFalse(ok, msg)

    def test_unsigned_authority_fails_consistency(self):
        self.assertIn("without an operator signature", gatekeeper.signature_error(self._approved()))

    def test_signed_authority_passes_and_tampering_fails(self):
        signed = gatekeeper.sign_state(self._approved(), self.key.read_bytes().strip())
        self.assertEqual(gatekeeper.signature_error(signed), "")
        signed["deployment_authorized"] = True
        self.assertIn("does not match", gatekeeper.signature_error(signed))

    def test_forged_self_consistent_state_does_not_authorize_writes(self):
        import json
        gatekeeper.GATE_STATE.write_text(json.dumps(self._approved()))
        ok, _ = gatekeeper.check_action("write", "src/app.py")
        self.assertFalse(ok)

    def test_signed_state_on_disk_authorizes_source_write(self):
        import json
        signed = gatekeeper.sign_state(self._approved(), self.key.read_bytes().strip())
        gatekeeper.GATE_STATE.write_text(json.dumps(signed))
        ok, msg = gatekeeper.check_action("write", "src/app.py")
        self.assertTrue(ok, msg)

    def test_key_inside_project_is_refused(self):
        inside = self.root / "operator.key"
        inside.write_text("k" * 64)
        os.environ[gatekeeper.OPERATOR_KEY_ENV] = str(inside)
        signed = gatekeeper.sign_state(self._approved(), inside.read_bytes())
        self.assertIn("inside the project", gatekeeper.signature_error(signed))

    def test_draft_state_needs_no_signature(self):
        self.assertEqual(gatekeeper.signature_error({"approval_state": "draft"}), "")


class WriteAuditTests(unittest.TestCase):
    """JER-37: the post-dispatch write audit can't be evaded or skipped."""

    def test_rename_into_protected_source_seen_at_destination(self):
        paths = governed_factory._porcelain_paths(b"R  src/app.py\0docs/x.md\0?? notes.txt\0")
        self.assertEqual(paths, {"src/app.py", "docs/x.md", "notes.txt"})

    def test_git_mv_into_protected_source_is_flagged(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
            (root / "docs").mkdir()
            (root / "src").mkdir()
            (root / "docs/x.md").write_text("x\n")
            for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "init"]):
                subprocess.run(git + args, cwd=root, check=True, capture_output=True)
            saved = governed_factory.ROOT
            governed_factory.ROOT = root
            try:
                before = governed_factory.working_tree_snapshot()
                subprocess.run(git + ["mv", "docs/x.md", "src/app.py"], cwd=root, check=True)
                after = governed_factory.working_tree_changes()
            finally:
                governed_factory.ROOT = saved
            self.assertIn("src/app.py", governed_factory.unauthorized_writes(before, after, {}))

    def test_authority_store_change_flagged_even_when_authorized(self):
        viol = governed_factory.unauthorized_writes(
            set(), {".governance/gate_state.json", "src/app.py"}, {"implementation_authorized": True})
        self.assertEqual(viol, [".governance/gate_state.json"])

    def test_non_planning_paths_flagged(self):
        viol = governed_factory.unauthorized_writes(
            set(), {"automation/gatekeeper.py", "docs/notes.md"}, {"implementation_authorized": False})
        self.assertEqual(viol, ["automation/gatekeeper.py"])

    def test_changed_preexisting_dirt_is_attributed(self):
        saved = governed_factory._fingerprint
        try:
            governed_factory._fingerprint = lambda path: "after"
            viol = governed_factory.unauthorized_writes(
                {"src/app.py": "before"}, {"src/app.py"}, {"implementation_authorized": False})
            self.assertEqual(viol, ["src/app.py"])
            governed_factory._fingerprint = lambda path: "before"
            viol = governed_factory.unauthorized_writes(
                {"src/app.py": "before"}, {"src/app.py"}, {"implementation_authorized": False})
            self.assertEqual(viol, [])
        finally:
            governed_factory._fingerprint = saved


if __name__ == "__main__":
    unittest.main()
