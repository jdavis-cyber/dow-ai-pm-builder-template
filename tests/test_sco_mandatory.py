"""JER-24: the Security & Compliance Officer is mandatory on every project."""
import json, pathlib, shutil, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


class SecurityComplianceOfficerMandatoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.copy = pathlib.Path(self.tmp.name) / "template"
        shutil.copytree(ROOT, self.copy, ignore=shutil.ignore_patterns(".git", ".codex", ".claude", "__pycache__"))

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        return run(sys.executable, str(self.copy / "automation/validate_template.py"), cwd=self.copy)

    def test_sco_is_a_global_package(self):
        self.assertTrue((ROOT / "subagents/global/security-compliance-officer.toml").exists())
        self.assertFalse((ROOT / "subagents/dod-regulated/security-compliance-officer.toml").exists())
        matrix = (ROOT / "directives/agent-activation-matrix.md").read_text(encoding="utf-8")
        row = next(line for line in matrix.splitlines() if line.startswith("| `security-compliance-officer`"))
        self.assertIn("| `global` | Yes |", row)

    def test_sco_mandatory_in_runtime_for_unregulated_project(self):
        cfg = json.loads((ROOT / "subagents/install-config.json").read_text(encoding="utf-8"))
        self.assertNotEqual(cfg.get("requires_dod_controls"), True)
        runtime = pathlib.Path(self.tmp.name) / "runtime"
        r = run(sys.executable, "automation/install_subagents.py", "subagents/install-config.json", str(runtime))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        manifest = json.loads((runtime / "runtime-manifest.json").read_text(encoding="utf-8"))
        sco = next(a for a in manifest["accountable_agents"] if a["name"] == "security-compliance-officer")
        self.assertTrue(sco["mandatory"])
        self.assertEqual(sco["tier"], "global")

    def test_validation_fails_when_sco_is_made_conditional(self):
        cfg_path = self.copy / "subagents/install-config.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["mandatory_agents"] = [a for a in cfg["mandatory_agents"] if a != "security-compliance-officer"]
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        r = self.validate()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("security not mandatory", r.stdout)

    def test_validation_fails_when_sco_moves_back_to_overlays(self):
        (self.copy / "subagents/global/security-compliance-officer.toml").rename(
            self.copy / "subagents/dod-regulated/security-compliance-officer.toml")
        r = self.validate()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("must be a global package", r.stdout)

    def test_validation_fails_when_sco_missing_from_roster(self):
        roster = self.copy / ".agent/AGENT-ROSTER.md"
        roster.write_text(roster.read_text(encoding="utf-8").replace("security-compliance-officer", "removed-officer"), encoding="utf-8")
        r = self.validate()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("roster missing security-compliance-officer", r.stdout)


if __name__ == "__main__":
    unittest.main()
