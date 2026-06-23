#!/usr/bin/env python3
import json, pathlib, subprocess, sys, tempfile, shutil
ROOT=pathlib.Path(__file__).resolve().parent.parent
ACCOUNTABLE=["requirements-ba","user-story-ba","ui-ux-designer","architecture-se","database-engineer","backend-developer","frontend-developer","pipeline-devops","performance-devops","qa-engineer","automation-test-engineer","scrum-master","program-analyst","documentation-se","security-compliance-officer"]
def run(cmd):
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    if r.returncode!=0: print(r.stdout+r.stderr)
    return r.returncode==0
def main():
    ok=True
    souls=sorted(p.stem for p in (ROOT/'.agent/souls').glob('*.md'))
    if souls!=sorted(ACCOUNTABLE): print('ERROR: SOUL roster mismatch', souls); ok=False
    roster=(ROOT/'.agent/AGENT-ROSTER.md').read_text()
    for n in ACCOUNTABLE:
        if n not in roster: print('ERROR: roster missing '+n); ok=False
    cfg=json.loads((ROOT/'subagents/install-config.json').read_text())
    if cfg.get('accountable_agents')!=ACCOUNTABLE: print('ERROR: install-config accountable_agents mismatch'); ok=False
    if 'security-compliance-officer' not in cfg.get('mandatory_agents',[]): print('ERROR: security not mandatory'); ok=False
    own=json.loads((ROOT/'subagents/specialization-ownership-map.json').read_text())
    tomls=sorted(str(p.relative_to(ROOT/'subagents')).replace('\\','/') for p in (ROOT/'subagents/global/voltagent').glob('**/*.toml'))
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
    stale=['14 specialized' + ' agents','complete AI development team - ' + '14','Template Version ' + '3.0']
    for p in ROOT.glob('**/*'):
        if p.is_file() and '.git' not in p.parts and p.suffix in {'.md','.py','.json','.toml','.yml','.yaml','.sh'}:
            txt=p.read_text(errors='ignore')
            for s in stale:
                if s in txt and p.name!='validate_template.py': print(f'ERROR stale string {s} in {p.relative_to(ROOT)}'); ok=False
    tmp_runtime = pathlib.Path(tempfile.mkdtemp(prefix='dow-template-runtime-'))
    try:
        ok = run([sys.executable,'automation/install_subagents.py','subagents/install-config.json',str(tmp_runtime)]) and ok
        ok = run([sys.executable,'automation/validate_runtime.py',str(tmp_runtime/'runtime-manifest.json')]) and ok
    finally:
        shutil.rmtree(tmp_runtime, ignore_errors=True)
    ok = run([sys.executable,'automation/validate_spec.py','--mode','template','orchestration/system-spec-template.md']) and ok
    ok = run([sys.executable,'automation/validate_tasks.py','orchestration/task-board-template.md']) and ok
    if 'Reference Needed' not in (ROOT/'directives/templates/standards-crosswalk-matrix.md').read_text(): print('ERROR ISO 27701 not gap-labeled'); ok=False
    print('whole-template validation passed' if ok else 'whole-template validation failed')
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
