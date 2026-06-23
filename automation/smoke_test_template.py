#!/usr/bin/env python3
import pathlib, shutil, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
def run(cmd,cwd=ROOT):
    r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
    if r.returncode!=0: print(r.stdout+r.stderr); raise SystemExit(r.returncode)
    return r.stdout.strip()
def main():
    parent=pathlib.Path(tempfile.mkdtemp(prefix='dow-template-smoke-'))
    try:
        run([sys.executable,'automation/init_project.py','smoke-project',str(parent)])
        project=parent/'smoke-project'
        assert (project/'.git').exists(), 'git repo missing'
        assert run(['git','rev-parse','HEAD'], project), 'initial commit missing'
        manifest=project/'.codex/agents/runtime-manifest.json'
        assert manifest.exists(), 'runtime manifest missing'
        run([sys.executable,str(project/'automation/validate_runtime.py'),str(manifest)], project)
        for d in ['.governance','docs/verification','docs/handoff','docs/product','docs/architecture','docs/governance-frameworks','orchestration']:
            assert (project/d).exists(), f'missing {d}'
        kickoff=(project/'KICKOFF.md').read_text()
        assert 'Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.' in kickoff, 'kickoff protocol missing canonical phrase'
        readme=(project/'README.md').read_text()
        assert 'Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.' in readme, 'generated README missing canonical kickoff phrase'
        run([sys.executable,str(project/'automation/validate_spec.py'),'--mode','draft',str(project/'orchestration/system_spec.md')], project)
        run([sys.executable,str(project/'automation/gatekeeper.py'),'verify-consistency'], project)
        factory_output=run([sys.executable,str(project/'automation/governed_factory.py'),'--adapter','assisted'], project)
        assert 'NEXT GOVERNED FACTORY TASK: TASK-001' in factory_output, 'governed factory did not select TASK-001'
        assert 'Provider-neutral factory contract' in factory_output, 'factory output missing provider-neutral contract'
        assert 'implementation_authorized' in factory_output, 'factory output missing gate authority state'
        assert (project/'factory.config.example.json').exists(), 'generated project missing factory config example'
        factory_sh=(project/'automation/factory.sh').read_text()
        assert 'LLM_COMMAND' not in factory_sh, 'generated factory.sh still uses LLM_COMMAND'
        assert 'FACTORY_ADAPTER' in factory_sh, 'generated factory.sh missing adapter interface'
        print('golden-path smoke test passed')
    finally:
        shutil.rmtree(parent, ignore_errors=True)
if __name__=='__main__': main()
