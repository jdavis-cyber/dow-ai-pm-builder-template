"""AI-1152: locked specs reject every unresolved status label, and the
dispatcher runs Lock 0 itself instead of trusting a verify.md.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_commit_audit import ShellAdapterFixture  # noqa: E402
import governed_factory  # noqa: E402
import validate_spec  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOCK0 = "`python3 automation/validate_spec.py --mode locked orchestration/system_spec.md`"


def resolved_spec() -> str:
    """The spec template with every placeholder answered, as Lock 0 expects."""
    text = (ROOT / "orchestration/system-spec-template.md").read_text()
    text = text.replace("[Draft / Validated]", "Validated")
    return validate_spec.PLACEHOLDER_RE.sub("synthetic value", text)


class LockedLabelTests(unittest.TestCase):
    UNRESOLVED = [
        "Draft", "Status: Draft", "**Status**: Draft", "(Draft)", "Status: draft", "Status: Draft / Validated",
        "Not Approved", "Approval: not approved",
        "N/A", "Deadline: N/A", "- **Deadline**: n/a", "| Export controls | N/A |",
        "gap - owner decision outstanding", "Purpose: gap: owner decision outstanding",
        "Purpose: Gap owner unknown", "Gap owner unknown",
        "Draft v0.3", "Status: Draft v2", "Status: Draft 1.2", "Status: Draft (2026-10-01)", "Status: Draft 2026-10-01",
        "Status: Validated / Draft", "Status: Draft — awaiting review", "[Draft]", "| Status | Draft |",
        "Approval: Not Approved", "Approval: Not Approved (2026-10-01)", "Purpose: Gap — decision outstanding",
    ]
    RESOLVED = [
        "Deadline: N/A — continuous delivery, no contractual date",
        "Section 508: N/A because the system ships no user interface",
        "Air gap isolates the synthetic system", "Air gap - enforced by the enclave",
        "Gap analysis completed", "No gap remains", "Gapless record sequence",
        "The drafting committee reviewed scope", "A draft of the report is reviewed weekly",
        "Data not approved for release is excluded from training",
        "Approved by the Director on 2026-10-01", "**Status**: Validated",
        # Codex P2 on #28: an imperative "Draft" is an instruction, not a status.
        "- **Output Contract**: Draft user stories from approved requirements.",
        "Purpose: Draft legislation tracking for counsel", "Draft the release notes after Gate 2.",
        "Not Approved requests return to the requester with reasons.",
        "Gap closure plan approved by the Director", "Gap owner: Requirements BA (resolved 2026-10-01)", "Draft 3 user stories per sprint",
    ]

    def check(self, text):
        path = Path(self.tmp) / "spec.md"
        path.write_text(text)
        return subprocess.run([sys.executable, str(ROOT / "automation/validate_spec.py"), "--mode", "locked", str(path)],
                              capture_output=True, text=True)

    def setUp(self):
        import tempfile
        self._td = tempfile.TemporaryDirectory()
        self.tmp = self._td.name

    def tearDown(self):
        self._td.cleanup()

    def test_unresolved_labels_fail_locked_mode(self):
        for value in self.UNRESOLVED:
            with self.subTest(value=value):
                result = self.check("Purpose: record synthetic notes\n" + value + "\n")
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("lock readiness line 2", result.stdout)

    def test_resolved_prose_passes_locked_mode(self):
        for value in self.RESOLVED:
            with self.subTest(value=value):
                result = self.check(value + "\n")
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_filled_template_passes_and_raw_template_fails(self):
        self.assertEqual(validate_spec.locked_problems(resolved_spec()), [])
        self.assertTrue(validate_spec.locked_problems((ROOT / "orchestration/system-spec-template.md").read_text()))

    def test_lock0_task_detection(self):
        detect = governed_factory.lock0_spec_paths
        self.assertEqual(detect({"Verification Command or Method": LOCK0}), ["orchestration/system_spec.md"])
        self.assertEqual(detect({"Verification Command or Method": "`python3 automation/validate_spec.py docs/x.md`"}),
                         ["docs/x.md", "orchestration/system_spec.md"])
        self.assertEqual(detect({"Title": "Lock 0: validate the system specification"}),
                         ["orchestration/system_spec.md"])
        self.assertEqual(detect({"Verification Command or Method":
                                 "python3 automation/validate_spec.py --mode template orchestration/x.md"}), [])
        self.assertEqual(detect({"Verification Command or Method": "local fixture check"}), [])

    def test_shell_redirections_are_not_spec_paths(self):
        # Codex P2 on #28: "> verify.md" was read as two spec paths.
        spec = "orchestration/system_spec.md"
        for tail in ["> docs/verification/TASK-009/verify.md", ">> docs/v.md", "2> err.txt", "&> all.txt",
                     "< /dev/null", "1> out.txt", "2>&1", "> out.txt 2>&1", ">docs/v.md", "2>err.txt",
                     ">>docs/v.md", "&>all.txt", "<in.txt", "2>&1 > out.txt"]:
            with self.subTest(tail=tail):
                command = f"`python3 automation/validate_spec.py --mode locked {spec} {tail}`"
                self.assertEqual(governed_factory.lock0_spec_paths({"Verification Command or Method": command}),
                                 [spec])
        attached = f"python3 automation/validate_spec.py --mode locked {spec}>docs/v.md"
        self.assertEqual(governed_factory.lock0_spec_paths({"Verification Command or Method": attached}), [spec])
        redirected = {"Verification Command or Method":
                      f"python3 automation/validate_spec.py --mode locked {spec} > docs/verification/TASK-009/verify.md"}
        problems = governed_factory.lock0_problems(governed_factory.lock0_spec_paths(redirected))
        self.assertFalse([p for p in problems if not p.startswith(spec + ":")], problems)

    def test_quoted_validator_commands_keep_their_paths(self):
        # Codex P2 on #29/#30: stripping the script prefix from a quoted
        # command left a stray quote, shlex.split failed, and the fallback
        # returned quote-bearing paths that lock0_problems reported missing.
        spec = "orchestration/system_spec.md"
        detect = governed_factory.lock0_spec_paths
        cases = {
            f'python3 "automation/validate_spec.py" --mode locked "{spec}"': [spec],
            f"python3 'automation/validate_spec.py' --mode 'locked' '{spec}'": [spec],
            f"python3 automation/validate_spec.py --mode locked {spec}": [spec],
            f'`python3 "automation/validate_spec.py" --mode locked "{spec}"`': [spec],
            f'python3 "automation/validate_spec.py" --mode=locked "{spec}" > "docs/v.md"': [spec],
            'python3 automation/validate_spec.py --mode locked "docs/my spec.md"': ["docs/my spec.md", spec],
            f'python3 "automation/validate_spec.py" --mode locked "{spec}"; echo "done"': [spec],
            f"python3 'automation/validate_spec.py' --mode 'template' '{spec}'": [],
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(detect({"Verification Command or Method": command}), expected)
        for command in list(cases)[:3]:
            with self.subTest(problems=command):
                problems = governed_factory.lock0_problems(detect({"Verification Command or Method": command}))
                self.assertFalse([p for p in problems if not p.startswith(spec + ":")], problems)

    def test_windows_backslash_paths_survive(self):
        # Codex P2 on #28 round 2 (4410860851): POSIX shlex dropped the
        # backslashes, so orchestration\system_spec.md became
        # orchestrationsystem_spec.md and Lock 0 reported the spec missing.
        spec = "orchestration/system_spec.md"
        detect = governed_factory.lock0_spec_paths
        cases = {
            r"python automation\validate_spec.py --mode locked orchestration\system_spec.md": [spec],
            r'python "C:\repo\automation\validate_spec.py" --mode locked "docs\my spec.md"':
                ["docs/my spec.md", spec],
            r"py 'automation\validate_spec.py' --mode 'locked' 'orchestration\system_spec.md'": [spec],
            r"python automation/validate_spec.py --mode locked orchestration\sub/x.md": ["orchestration/sub/x.md", spec],
            r"python automation\validate_spec.py --mode locked docs/a\b.md > docs\v.md 2>&1": ["docs/a/b.md", spec],
            r"`python automation\validate_spec.py --mode template orchestration\system_spec.md`": [],
            # A POSIX escaped space is still an escape, not a path separator.
            r"python3 automation/validate_spec.py --mode locked docs/my\ spec.md": ["docs/my spec.md", spec],
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(detect({"Verification Command or Method": command}), expected)
        windows = r"python automation\validate_spec.py --mode locked orchestration\system_spec.md"
        problems = governed_factory.lock0_problems(detect({"Verification Command or Method": windows}))
        self.assertFalse([p for p in problems if not p.startswith(spec + ":")], problems)


class DispatcherLock0Tests(ShellAdapterFixture, unittest.TestCase):
    def lock0_board(self, status="Ready", follower=False):
        board = self.repo / "orchestration/tasks.md"
        text = board.read_text().replace("**Verification Command or Method**: local fixture check",
                                         f"**Verification Command or Method**: {LOCK0}")
        text = text.replace("**Status**: Ready", f"**Status**: {status}")
        if follower:
            follower_task = re.sub(r"TASK-901", "TASK-902", board.read_text())
            follower_task = follower_task.replace("**Dependencies**: None", "**Dependencies**: TASK-901")
            text += "\n" + follower_task
        board.write_text(text)

    def test_lock0_cannot_complete_on_an_unresolved_spec(self):
        self.lock0_board()
        result, record = self.run_adapter("")
        self.assert_violation(result, record, "lock 0 spec validation failed")
        self.assertTrue(record["checks"]["lock0_spec"]["problems"])

    def test_lock0_completes_on_a_resolved_spec(self):
        self.lock0_board()
        (self.repo / "orchestration/system_spec.md").write_text(resolved_spec())
        result, record = self.run_adapter("")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["checks"]["lock0_spec"], "pass")

    def test_task_after_lock0_is_not_dispatched_on_an_unresolved_spec(self):
        # TASK-901 (Lock 0) is already Done, e.g. on the strength of a verify.md alone.
        self.lock0_board(status="Done", follower=True)
        (self.repo / "adapter.py").write_text("raise SystemExit('adapter must not run')\n")
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        result = self.factory("shell")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("TASK-902 follows Lock 0", result.stdout)
        self.assertNotIn("NEXT GOVERNED FACTORY TASK", result.stdout)
        (self.repo / "orchestration/system_spec.md").write_text(resolved_spec())
        result = self.factory("assisted")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NEXT GOVERNED FACTORY TASK: TASK-902", result.stdout)


if __name__ == "__main__":
    unittest.main()
