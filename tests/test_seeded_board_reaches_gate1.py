"""JER-26: a fresh project can walk its seeded board to the Gate 1 decision.

Assisted mode only; the "human" completes each task by writing its evidence
and marking it Done, and the dispatcher's own checks run on every completion.
"""
import os, pathlib, re, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GIT_ENV = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}


class SeededBoardReachesGate1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        self.env.update(GIT_ENV, FACTORY_CHAIN_ANCHOR_DIR=str(pathlib.Path(self.tmp.name) / "anchors"))
        r = self.run_cmd(sys.executable, str(ROOT / "automation/init_project.py"), "gate-one", self.tmp.name, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.project = pathlib.Path(self.tmp.name) / "gate-one"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args, cwd=None):
        return subprocess.run(args, cwd=cwd or self.project, env=self.env, capture_output=True, text=True, timeout=120)

    def factory(self):
        return self.run_cmd(sys.executable, "automation/governed_factory.py", "--adapter", "assisted")

    def complete(self, task_id):
        board = self.project / "orchestration/tasks.md"
        text = board.read_text(encoding="utf-8")
        block = re.search(rf"#### {task_id}:.*?(?=\n#### |\Z)", text, re.S).group(0)
        evidence = re.findall(r"`([^`]+)`", re.search(r"\*\*Evidence Required\*\*: (.*)", block).group(1))
        for rel in evidence:
            path = self.project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Synthetic evidence for {task_id}\n", encoding="utf-8")
        if task_id == "TASK-009":
            # Lock 0: the dispatcher runs locked validation itself, so answer the spec.
            spec = self.project / "orchestration/system_spec.md"
            answered = spec.read_text(encoding="utf-8").replace("[Draft / Validated]", "Validated")
            spec.write_text(re.sub(r"(?<![!])\[[^\]]+\](?!\()", "synthetic value", answered), encoding="utf-8")
        done = re.sub(r"\*\*Status\*\*: \w+", "**Status**: Done", block, count=1)
        text = text.replace(block, done)
        # Dependent tasks become Ready once everything they wait on is Done.
        board.write_text(text, encoding="utf-8")

    def promote_ready(self):
        board = self.project / "orchestration/tasks.md"
        text = board.read_text(encoding="utf-8")
        done = set(re.findall(r"#### (TASK-\d+):[^\n]*\n(?:[^\n]*\n)*?\*\*Status\*\*: Done", text))
        for m in re.finditer(r"#### (TASK-\d+):.*?(?=\n#### |\Z)", text, re.S):
            block = m.group(0)
            deps = set(re.findall(r"TASK-\d+", re.search(r"\*\*Dependencies\*\*: (.*)", block).group(1)))
            if "**Status**: Pending" in block and deps <= done:
                text = text.replace(block, block.replace("**Status**: Pending", "**Status**: Ready", 1))
        board.write_text(text, encoding="utf-8")

    def test_seeded_board_is_schema_valid(self):
        for board in ["orchestration/task-board-template.md", "orchestration/tasks.md"]:
            r = subprocess.run([sys.executable, "automation/validate_tasks.py", board], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, board + r.stdout)

    def test_assisted_walk_stops_at_the_gate_1_decision(self):
        seen = []
        for _ in range(20):
            r = self.factory()
            out = r.stdout + r.stderr
            if "TASK-014 appears to require human" in out:
                break
            self.assertEqual(r.returncode, 0, out)
            m = re.search(r"NEXT GOVERNED FACTORY TASK: (TASK-\d+)", out)
            self.assertIsNotNone(m, out)
            seen.append(m.group(1))
            self.complete(m.group(1))
            self.promote_ready()
        else:
            self.fail(f"never reached the Gate 1 decision; dispatched {seen}")
        self.assertEqual(seen, [f"TASK-{n:03d}" for n in range(1, 14)])
        results = list((self.project / "docs/verification/factory-runs").glob("*-result.json"))
        self.assertEqual(len(results), 13)  # TASK-013 is checked on the run that stops at TASK-014
        import json
        self.assertTrue(all(json.loads(p.read_text(encoding="utf-8"))["outcome"] == "pass" for p in results))


if __name__ == "__main__":
    unittest.main()
