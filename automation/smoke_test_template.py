#!/usr/bin/env python3
import os, pathlib, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
def run(cmd, cwd=ROOT, *, env=None):
    r=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,errors="replace")
    if r.returncode!=0: print(r.stdout+r.stderr); raise SystemExit(r.returncode)
    return r.stdout.strip()
def main():
    with tempfile.TemporaryDirectory(prefix=".dow-template-smoke-", dir=ROOT) as directory:
        parent = pathlib.Path(directory)
        # The smoke project and its disposable operator are siblings. A sandboxed
        # smoke run must neither use live seals nor require the user's signing key.
        env = {key: value for key, value in os.environ.items() if not key.startswith(("FACTORY_", "GIT_"))}
        env.update(
            FACTORY_CHAIN_ANCHOR_DIR=str(parent / "operator-chains"),
            FACTORY_OPERATOR_KEY_FILE=str(parent / "unused-operator.key"),
            TMPDIR=directory, TMP=directory, TEMP=directory,
            GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Smoke fixture", GIT_COMMITTER_NAME="Smoke fixture",
            GIT_AUTHOR_EMAIL="smoke@example.invalid", GIT_COMMITTER_EMAIL="smoke@example.invalid",
        )
        run([sys.executable,'automation/init_project.py','smoke-project',str(parent),'--smoke-fixture'], env=env)
        project=parent/'smoke-project'
        assert (project/'.git').exists(), 'git repo missing'
        assert run(['git','rev-parse','HEAD'], project, env=env), 'initial commit missing'
        manifest=project/'.codex/agents/runtime-manifest.json'
        assert manifest.exists(), 'runtime manifest missing'
        run([sys.executable,str(project/'automation/validate_runtime.py'),str(manifest)], project, env=env)
        for d in ['.governance','docs/verification','docs/handoff','docs/product','docs/architecture','orchestration']:
            assert (project/d).exists(), f'missing {d}'
        kickoff=(project/'KICKOFF.md').read_text(encoding="utf-8")
        assert 'Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.' in kickoff, 'kickoff protocol missing canonical phrase'
        readme=(project/'README.md').read_text(encoding="utf-8")
        assert 'Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.' in readme, 'generated README missing canonical kickoff phrase'
        run([sys.executable,str(project/'automation/validate_spec.py'),'--mode','draft',str(project/'orchestration/system_spec.md')], project, env=env)
        run([sys.executable,str(project/'automation/gatekeeper.py'),'verify-consistency'], project, env=env)
        factory_output=run([sys.executable,str(project/'automation/governed_factory.py'),'--adapter','assisted'], project, env=env)
        assert 'NEXT GOVERNED FACTORY TASK: TASK-001' in factory_output, 'governed factory did not select TASK-001'
        assert 'Provider-neutral factory contract' in factory_output, 'factory output missing provider-neutral contract'
        assert 'implementation_authorized' in factory_output, 'factory output missing gate authority state'
        assert (project/'factory.config.example.json').exists(), 'generated project missing factory config example'
        factory_sh=(project/'automation/factory.sh').read_text(encoding="utf-8")
        assert 'LLM_COMMAND' not in factory_sh, 'generated factory.sh still uses LLM_COMMAND'
        assert 'FACTORY_ADAPTER' in factory_sh, 'generated factory.sh missing adapter interface'
        print('golden-path smoke test passed')
if __name__ == '__main__':
    # Survive a console that is not UTF-8, e.g. cp1252 on Windows (AI-1151).
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    sys.dont_write_bytecode = True  # leave no __pycache__ behind in the project
    import safe_console
    safe_console.make_console_safe()
    main()
