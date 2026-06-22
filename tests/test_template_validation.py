import json, pathlib, subprocess, sys, tempfile, shutil, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
ACCOUNTABLE=["requirements-ba","user-story-ba","ui-ux-designer","architecture-se","database-engineer","backend-developer","frontend-developer","pipeline-devops","performance-devops","qa-engineer","automation-test-engineer","scrum-master","program-analyst","documentation-se","security-compliance-officer"]
def run(*args, cwd=ROOT): return subprocess.run(args,cwd=cwd,capture_output=True,text=True)
class TemplateValidationTests(unittest.TestCase):
    def test_roster_and_souls(self):
        self.assertEqual(sorted(p.stem for p in (ROOT/'.agent/souls').glob('*.md')), sorted(ACCOUNTABLE))
        roster=(ROOT/'.agent/AGENT-ROSTER.md').read_text()
        for a in ACCOUNTABLE: self.assertIn(a, roster)
    def test_runtime_install_and_validate(self):
        tmp=pathlib.Path(tempfile.mkdtemp())
        try:
            r=run(sys.executable,'automation/install_subagents.py','subagents/install-config.json',str(tmp)); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            m=json.loads((tmp/'runtime-manifest.json').read_text())
            self.assertEqual([a['name'] for a in m['accountable_agents']], ACCOUNTABLE)
            self.assertTrue(next(a for a in m['accountable_agents'] if a['name']=='security-compliance-officer')['mandatory'])
            r=run(sys.executable,'automation/validate_runtime.py',str(tmp/'runtime-manifest.json')); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        finally: shutil.rmtree(tmp, ignore_errors=True)
    def test_specialization_ownership_covers_voltagent(self):
        own=json.loads((ROOT/'subagents/specialization-ownership-map.json').read_text())
        tomls=sorted(str(p.relative_to(ROOT/'subagents')).replace('\\','/') for p in (ROOT/'subagents/global/voltagent').glob('**/*.toml'))
        self.assertEqual(len(tomls),136); self.assertFalse([t for t in tomls if t not in own])
    def test_spec_modes_and_template_validator(self):
        self.assertEqual(run(sys.executable,'automation/validate_spec.py','--mode','template','orchestration/system-spec-template.md').returncode,0)
        self.assertEqual(run(sys.executable,'automation/validate_template.py').returncode,0)
    def test_kickoff_protocol_exists_and_is_operator_concise(self):
        kickoff=ROOT/'KICKOFF.md'
        self.assertTrue(kickoff.exists(), 'KICKOFF.md must be present at template root')
        txt=kickoff.read_text()
        self.assertIn('Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.', txt)
        self.assertNotIn('Start a new project from the DoW AI PM Builder Template.\n', txt)
        self.assertIn('canonical operator phrase', txt.lower())
        self.assertIn('Sprint Zero / Phase 0', txt)
        self.assertIn('stop at Gate 1 readiness', txt)
        self.assertIn('The interview owns discovery details', txt)
        self.assertIn('project name/path', txt)
        self.assertIn('files, links', txt)
        self.assertIn('authority boundaries', txt)
    def test_golden_path_smoke(self):
        r=run(sys.executable,'automation/smoke_test_template.py'); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__': unittest.main()
