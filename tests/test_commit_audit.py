"""AI-1153: the post-dispatch write audit also covers what the adapter commits.

Comparing only ``git status`` before and after a run let an adapter write a
protected path, ``git commit`` it, and leave a clean tree: the run passed.
These probes run the real shell adapter in a disposable copy of the template.
"""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
os.environ.setdefault("FACTORY_CHAIN_ANCHOR_DIR", tempfile.mkdtemp(prefix="dow-chain-anchor-"))

import governed_factory  # noqa: E402

GIT = "import subprocess\ndef git(*a):\n    subprocess.run(['git', *a], check=True, capture_output=True)\n"
COMMIT_ALL = "git('add', '-A'); git('commit', '-qm', 'adapter work')\n"


class ShellAdapterFixture:
    """A disposable copy of the template with one Ready task for a shell adapter."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dow-commit-audit-")
        self.repo = Path(self.tmp.name) / "fixture"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(
            ".git", ".codex", "__pycache__", ".pytest_cache", "requirement-remediation"))
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        self.env["FACTORY_CHAIN_ANCHOR_DIR"] = str(Path(self.tmp.name) / "chain-anchors")
        self.env.update(GIT_AUTHOR_NAME="Commit Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                        GIT_COMMITTER_NAME="Commit Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        task = {"Task ID": "TASK-901", "Phase": "Discovery", "Status": "Ready",
                "Owner Agent": "Requirements BA", "Required Inputs": "synthetic request",
                "Dependencies": "None", "Acceptance Criteria": "record synthetic notes",
                "Evidence Required": "`docs/verification/fixture.md`",
                "Verification Command or Method": "local fixture check",
                "Handoff Target": "User Story BA", "Gate Impact": "none", "Requires Authority": "none"}
        (self.repo / "orchestration/tasks.md").write_text(
            "#### TASK-901: Synthetic documentation task\n"
            + "\n".join(f"**{k}**: {v}" for k, v in task.items()) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              capture_output=True, text=True, check=True).stdout.strip()

    def run_adapter(self, body, extra_commits=0, complete=True):
        """Commit the fixture, then dispatch one task to a shell adapter running ``body``.

        Unless ``complete`` is false, the adapter writes the task's evidence and
        closes it first, so a run that does nothing else passes.
        """
        code = "import pathlib\n" + GIT
        if complete:
            code += ("pathlib.Path('docs/verification/fixture.md').write_text('Synthetic verification only\\n')\n"
                     "p = pathlib.Path('orchestration/tasks.md')\n"
                     "p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))\n")
        code += body
        (self.repo / "adapter.py").write_text(code)
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "synthetic fixture")
        for n in range(extra_commits):
            (self.repo / "docs" / f"history-{n}.md").write_text(f"history {n}\n")
            self.git("add", "-A")
            self.git("commit", "-qm", f"history {n}")
        result = self.factory("shell")
        records = list((self.repo / "docs/verification/factory-runs").glob("*-result.json"))
        self.assertEqual(len(records), 1, result.stdout + result.stderr)
        return result, json.loads(records[0].read_text())

    def factory(self, adapter):
        command = shlex.join([sys.executable, "adapter.py"])
        return subprocess.run([sys.executable, "automation/governed_factory.py", "--adapter", adapter],
                              cwd=self.repo, env={**self.env, "FACTORY_ADAPTER_COMMAND": command},
                              capture_output=True, text=True, timeout=60)

    def assert_violation(self, result, record, kind):
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertNotEqual(record["outcome"], "pass")
        self.assertIn(kind, record["violations"])


class AdapterCommitAuditTests(ShellAdapterFixture, unittest.TestCase):
    def assert_committed_write_flagged(self, path, body):
        result, record = self.run_adapter(body + COMMIT_ALL)
        self.assert_violation(result, record, "unauthorized writes")
        self.assert_violation(result, record, "adapter commit")
        self.assertIn(path, record["checks"]["write_audit"]["violations"])
        audit = record["checks"]["commit_audit"]
        self.assertIn(path, audit["changed_paths"])
        self.assertEqual((audit["new_commit_count"], len(audit["new_commits"])), (1, 1))
        # The tree is clean afterwards: only the commit comparison sees the write.
        self.assertEqual(self.git("status", "--porcelain", "--", path), "")

    def test_committed_protected_source_is_flagged(self):
        self.assert_committed_write_flagged(
            "src/evil.py",
            "pathlib.Path('src').mkdir(exist_ok=True); pathlib.Path('src/evil.py').write_text('x = 1\\n')\n")

    def test_committed_factory_code_edit_is_flagged(self):
        self.assert_committed_write_flagged(
            "automation/gatekeeper.py",
            "g = pathlib.Path('automation/gatekeeper.py'); g.write_text(g.read_text() + '\\n# changed\\n')\n")

    def test_committed_gate_state_change_is_flagged(self):
        self.assert_committed_write_flagged(
            ".governance/gate_state.json",
            "import json\ns = pathlib.Path('.governance/gate_state.json')\n"
            "d = json.loads(s.read_text()); d['implementation_authorized'] = True\n"
            "s.write_text(json.dumps(d))\n")

    def test_commit_of_in_scope_files_is_still_a_violation(self):
        # No task authority grants commits, so any adapter commit fails closed.
        result, record = self.run_adapter(COMMIT_ALL)
        self.assert_violation(result, record, "adapter commit")
        self.assertNotIn("unauthorized writes", record["violations"])
        self.assertEqual(record["checks"]["write_audit"], "pass")

    def test_reset_to_an_ancestor_is_history_rewrite(self):
        result, record = self.run_adapter("git('reset', '-q', '--soft', 'HEAD~1')\n", extra_commits=1)
        self.assert_violation(result, record, "history rewritten")
        self.assertTrue(record["checks"]["commit_audit"]["history_rewritten"])

    def test_amend_is_history_rewrite_and_its_paths_are_audited(self):
        body = ("pathlib.Path('src').mkdir(exist_ok=True); pathlib.Path('src/evil.py').write_text('x = 1\\n')\n"
                "git('add', '-A'); git('commit', '-q', '--amend', '-m', 'rewritten')\n")
        result, record = self.run_adapter(body, extra_commits=1)
        self.assert_violation(result, record, "history rewritten")
        self.assert_violation(result, record, "unauthorized writes")
        self.assertIn("src/evil.py", record["checks"]["write_audit"]["violations"])

    def test_commit_on_side_branch_then_switch_back_is_flagged(self):
        body = ("git('checkout', '-q', '-b', 'side')\n"
                "pathlib.Path('src').mkdir(exist_ok=True); pathlib.Path('src/evil.py').write_text('x = 1\\n')\n"
                "git('add', 'src/evil.py'); git('commit', '-qm', 'side work'); git('checkout', '-q', '-')\n")
        result, record = self.run_adapter(body)
        self.assert_violation(result, record, "git refs changed")
        self.assertIn("refs/heads/side", record["checks"]["commit_audit"]["refs_changed"])

    def test_stashed_write_is_flagged(self):
        body = ("g = pathlib.Path('automation/gatekeeper.py'); g.write_text(g.read_text() + '\\n# changed\\n')\n"
                "git('stash', 'push', '-q', '--', 'automation/gatekeeper.py')\n")
        result, record = self.run_adapter(body)
        self.assert_violation(result, record, "git refs changed")
        self.assertIn("refs/stash", record["checks"]["commit_audit"]["refs_changed"])

    def test_run_without_git_changes_passes_commit_audit(self):
        result, record = self.run_adapter("")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["outcome"], "pass")
        self.assertEqual(record["checks"]["commit_audit"], "pass")


class GitStateUnitTests(unittest.TestCase):
    def test_missing_commit_baseline_fails_closed(self):
        record, kinds, paths = governed_factory.commit_audit(None, {"head": "", "refs": {}})
        self.assertEqual((kinds, paths), (["commit audit unavailable"], set()))
        self.assertTrue(record.startswith("fail"))
        record, kinds, paths = governed_factory.commit_audit({"head": "", "refs": {}}, None)
        self.assertEqual(kinds, ["commit audit unavailable"])

    def test_unchanged_state_passes(self):
        state = {"head": "a" * 40, "refs": {"refs/heads/main": "a" * 40}}
        self.assertEqual(governed_factory.commit_audit(state, dict(state)), ("pass", [], set()))


if __name__ == "__main__":
    unittest.main()
