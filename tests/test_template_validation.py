import json, pathlib, re, subprocess, sys, tempfile, shutil, unittest
from urllib.parse import unquote, urlsplit
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

    def test_generated_maintenance_links_resolve(self):
        """Copied guidance must link to files delivered with the project."""
        with tempfile.TemporaryDirectory() as d:
            r = run(sys.executable, 'automation/init_project.py', 'link-check', d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            project = pathlib.Path(d) / 'link-check'
            for rel in ['directives/factory-governance-scope.md',
                        'docs/handoff/documentation-map.md']:
                source = project / rel
                links = re.findall(r'\[[^\]]*\]\(([^)]+)\)', source.read_text())
                self.assertTrue(any(urlsplit(link).path.endswith('repository-maintenance.md')
                                    for link in links), rel)
                for link in links:
                    target = urlsplit(link)
                    if target.scheme or target.netloc or not target.path:
                        continue
                    resolved = (source.parent / unquote(target.path)).resolve()
                    with self.subTest(source=rel, link=link):
                        self.assertTrue(resolved.is_relative_to(project.resolve()))
                        self.assertTrue(resolved.is_file(), f'{rel}: missing {link}')

    def test_optional_assurance_documents_do_not_gate_template_integrity(self):
        """An adopter can omit reference paperwork without breaking tooling."""
        with tempfile.TemporaryDirectory() as d:
            copy = pathlib.Path(d) / 'template'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.codex', '.claude', '__pycache__'))
            for name in ['factory-control-matrix.md', 'factory-soa.md',
                         'factory-risk-register.md', 'factory-objectives.md',
                         'model-supplier-criteria.md', 'factory-ai-policy.md']:
                (copy / 'docs/governance-frameworks' / name).unlink()
            (copy / 'directives/templates/standards-crosswalk-matrix.md').write_text(
                '# Standards applicability\n\nNo framework selected for this test project.\n')
            r = run(sys.executable, str(copy / 'automation/validate_template.py'), cwd=copy)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_authority_control_still_fails_template_validation(self):
        """Optional paperwork must not make a missing runtime safeguard pass."""
        with tempfile.TemporaryDirectory() as d:
            copy = pathlib.Path(d) / 'template'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.codex', '.claude', '__pycache__'))
            gatekeeper = copy / 'automation/gatekeeper.py'
            gatekeeper.write_text(gatekeeper.read_text().replace(
                'deployment_authorized', 'deployment_control_removed_for_test'))
            r = run(sys.executable, str(copy / 'automation/validate_template.py'), cwd=copy)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('gatekeeper missing authority token deployment_authorized', r.stdout)
    def test_agent_packages_do_not_pin_a_model(self):
        """The operator picks model and effort per session, not the packages."""
        with tempfile.TemporaryDirectory() as d:
            copy = pathlib.Path(d) / 'template'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.codex', '.claude', '__pycache__'))
            r = run(sys.executable, str(copy / 'automation/validate_template.py'), cwd=copy)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            pkg = copy / 'subagents/global/requirements-ba.toml'
            pkg.write_text('model = "gpt-old"\n' + pkg.read_text())
            r = run(sys.executable, str(copy / 'automation/validate_template.py'), cwd=copy)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('pins model = "gpt-old"', r.stdout)
if __name__=='__main__': unittest.main()
