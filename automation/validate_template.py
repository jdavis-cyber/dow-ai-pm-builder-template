#!/usr/bin/env python3
import json, pathlib, subprocess, sys, tempfile, shutil
ROOT=pathlib.Path(__file__).resolve().parent.parent
ACCOUNTABLE=["requirements-ba","user-story-ba","ui-ux-designer","architecture-se","database-engineer","backend-developer","frontend-developer","pipeline-devops","performance-devops","qa-engineer","automation-test-engineer","scrum-master","program-analyst","documentation-se","security-compliance-officer"]
TEXT_SUFFIXES={'.md','.py','.json','.toml','.yml','.yaml','.sh'}
SKIP_DIRS={'.git','graphify-out','.claude','.codex','node_modules','venv','env','.pytest_cache','htmlcov'}
def template_files(rel='.'):
    """Files that make up the template under ``rel``.

    In a git checkout only tracked files count, so a workstation with untracked
    local files validates exactly like a clean clone. Outside git (an exported
    copy) every file is considered, minus local tool/cache directories.
    """
    base=(ROOT/rel).resolve()
    top=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=ROOT,capture_output=True,text=True)
    if top.returncode==0 and pathlib.Path(top.stdout.strip()).resolve()==ROOT.resolve():
        listed=subprocess.run(['git','ls-files','-z','--',str(base)],cwd=ROOT,capture_output=True,check=True)
        paths=[ROOT/f for f in listed.stdout.decode().split('\0') if f]
    else:
        paths=[p for p in base.glob('**/*') if not (SKIP_DIRS & set(p.relative_to(ROOT).parts))]
    return sorted(p for p in paths if p.is_file())
def run(cmd):
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    if r.returncode!=0: print(r.stdout+r.stderr)
    return r.returncode==0
def main():
    ok=True
    souls=sorted(p.stem for p in template_files('.agent/souls') if p.suffix=='.md' and p.parent==ROOT/'.agent/souls')
    if souls!=sorted(ACCOUNTABLE): print('ERROR: SOUL roster mismatch', souls); ok=False
    roster=(ROOT/'.agent/AGENT-ROSTER.md').read_text()
    for n in ACCOUNTABLE:
        if n not in roster: print('ERROR: roster missing '+n); ok=False
    cfg=json.loads((ROOT/'subagents/install-config.json').read_text())
    if cfg.get('accountable_agents')!=ACCOUNTABLE: print('ERROR: install-config accountable_agents mismatch'); ok=False
    if 'security-compliance-officer' not in cfg.get('mandatory_agents',[]): print('ERROR: security not mandatory'); ok=False
    own=json.loads((ROOT/'subagents/specialization-ownership-map.json').read_text())
    tomls=sorted(str(p.relative_to(ROOT/'subagents')).replace('\\','/') for p in template_files('subagents/global/voltagent') if p.suffix=='.toml')
    missing=[t for t in tomls if t not in own]
    if missing: print('ERROR: ownership missing '+str(missing[:5])); ok=False
    for f in ['CLAUDE.md','CODEX.md','GEMINI.md']:
        txt=(ROOT/f).read_text()
        if '15-agent' not in txt and '15 agent' not in txt.lower(): print('ERROR provider lacks 15-agent '+f); ok=False
        if 'Security & Compliance Officer' not in txt: print('ERROR provider lacks security '+f); ok=False
        if 'provider-neutral' not in txt or 'automation/governed_factory.py' not in txt: print('ERROR provider lacks governed factory startup '+f); ok=False
        if 'Protocal' in txt or ('Template Version ' + '3.0') in txt: print('ERROR stale provider text '+f); ok=False
    for rel in ['automation/governed_factory.py','automation/gatekeeper.py','factory.config.example.json']:
        if not (ROOT/rel).exists(): print('ERROR missing provider-neutral factory control '+rel); ok=False
    factory_sh=(ROOT/'automation/factory.sh').read_text()
    if 'LLM_COMMAND' in factory_sh: print('ERROR factory.sh still hardcodes LLM_COMMAND assisted-mode control'); ok=False
    if 'FACTORY_ADAPTER' not in factory_sh or 'automation/governed_factory.py' not in factory_sh: print('ERROR factory.sh missing adapter dispatcher'); ok=False
    gf=(ROOT/'automation/governed_factory.py').read_text()
    if 'Provider-neutral' not in gf and 'provider-neutral' not in gf: print('ERROR governed_factory missing provider-neutral contract'); ok=False
    if 'FACTORY_ADAPTER_COMMAND' not in gf: print('ERROR governed_factory missing shell adapter command hook'); ok=False
    gk=(ROOT/'automation/gatekeeper.py').read_text()
    for token in ['implementation_authorized','external_tracker_writes_authorized','deployment_authorized','control_closure_authorized']:
        if token not in gk: print('ERROR gatekeeper missing authority token '+token); ok=False
    cfg_example=json.loads((ROOT/'factory.config.example.json').read_text())
    if not cfg_example.get('factory',{}).get('provider_neutral_contract'): print('ERROR factory config missing provider-neutral contract flag'); ok=False
    kickoff=ROOT/'KICKOFF.md'
    if not kickoff.exists():
        print('ERROR missing KICKOFF.md'); ok=False
    else:
        kt=kickoff.read_text()
        for phrase in ['Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.', 'canonical operator phrase', 'Sprint Zero / Phase 0', 'stop at Gate 1 readiness', 'The interview owns discovery details', 'project name/path', 'files, links', 'authority boundaries']:
            if phrase not in kt: print('ERROR KICKOFF.md missing '+phrase); ok=False
    provider_bodies={f:(ROOT/f).read_text().split('\n',1)[1] for f in ['CLAUDE.md','CODEX.md','GEMINI.md']}
    if len(set(provider_bodies.values()))!=1: print('ERROR provider files out of sync (CLAUDE.md/CODEX.md/GEMINI.md must be identical below the title line)'); ok=False
    stale=['14 specialized' + ' agents','complete AI development team - ' + '14','Template Version ' + '3.0']
    for p in template_files():
        if p.suffix in TEXT_SUFFIXES:
            txt=p.read_text(errors='ignore')
            for s in stale:
                if s in txt and p.name!='validate_template.py': print(f'ERROR stale string {s} in {p.relative_to(ROOT)}'); ok=False
    tmp_runtime = pathlib.Path(tempfile.mkdtemp(prefix='dow-template-runtime-'))
    try:
        ok = run([sys.executable,'automation/install_subagents.py','subagents/install-config.json',str(tmp_runtime)]) and ok
        ok = run([sys.executable,'automation/validate_runtime.py',str(tmp_runtime/'runtime-manifest.json')]) and ok
    finally:
        shutil.rmtree(tmp_runtime, ignore_errors=True)
    ok = run([sys.executable,'automation/vendor_digests.py','check']) and ok
    ok = run([sys.executable,'automation/validate_spec.py','--mode','template','orchestration/system-spec-template.md']) and ok
    ok = run([sys.executable,'automation/validate_tasks.py','orchestration/task-board-template.md']) and ok
    # Framework crosswalks and duplicate assurance records are optional
    # reference material, not executable template-integrity requirements.
    if not (ROOT/'automation/factory_metrics.py').exists(): print('ERROR missing factory_metrics.py'); ok=False
    security=ROOT/'SECURITY.md'
    if not security.exists() or 'Incident communication' not in security.read_text(): print('ERROR SECURITY.md missing incident-communication path'); ok=False
    print('whole-template validation passed' if ok else 'whole-template validation failed')
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
