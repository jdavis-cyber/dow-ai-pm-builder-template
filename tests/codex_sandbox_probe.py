"""AI-1176 native sandbox acceptance test (no model/API calls).

Run from a normal operator terminal, outside an existing agent sandbox:
    python3 tests/codex_sandbox_probe.py --codex /path/to/codex

Requires Codex's `sandbox` interface. A missing client,
unsupported sandbox, or nested-sandbox refusal is a FAILURE, never a skip or
evidence that source protection worked. The probe creates disposable projects
and fixture authority records, without modifying the template's authority.
The override phase refreshes permissions with the operator command:
    python3 automation/codex_config.py codex-config
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]

# Run inside Codex's sandbox. Expecting PermissionError here is essential:
# failure to launch the sandbox must not masquerade as a refused source write.
PROBE = r'''
from pathlib import Path
import sys

authorized = sys.argv[1] == "write"
attempts = 0
def check_write(path, allowed):
    global attempts
    target = Path(path)
    original = target.read_bytes() if target.exists() else None
    try:
        target.write_text("sandbox probe\n")
    except PermissionError:
        assert not allowed, f"authorized write refused: {path}"
        assert (target.read_bytes() if target.exists() else None) == original
    else:
        assert allowed, f"UNAUTHORIZED WRITE SUCCEEDED: {path}"
    attempts += 1

for directory in ("src", "services", "packages", "database", "infrastructure", "execution"):
    check_write(f"{directory}/probe.py", authorized)
    check_write(f"{directory}/.gitkeep", authorized)
check_write("docs/planning-probe.md", authorized)
check_write(".codex/config.toml", False)
if not authorized:
    for path in (".governance/gate_state.json", ".governance/security-compliance/override-register.md",
                 "automation/gatekeeper.py", "AGENTS.md"):
        check_write(path, False)
check_write("docs/source-alias/alias-probe.py", authorized)
if not authorized:
    try:
        Path("docs/planning-probe.md").rename("src/renamed.py")
    except PermissionError:
        assert not Path("src/renamed.py").exists()
    else:
        raise AssertionError("rename bypassed source protection")
    attempts += 1
print(f"PASS: source={sys.argv[1]}, {attempts} write checks")
'''


def run(command, cwd, env=None):
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def probe(binary, project, access):
    (project / "docs/planning-probe.md").write_text("Operator fixture for the rename check.\n")
    alias = project / "docs/source-alias"
    if not alias.exists():
        alias.symlink_to("../src", target_is_directory=True)
    # Read the generated settings without changing user trust/config. Current
    # Codex's standalone sandbox command requires a built-in permission profile
    # corresponding to the configured legacy mode. This tests OS enforcement;
    # the interactive client's project-config loading still needs a live retest.
    config = tomllib.loads((project / ".codex/config.toml").read_text())
    settings = []
    for key, value in config.items():
        entries = value.items() if isinstance(value, dict) else [(None, value)]
        for subkey, entry in entries:
            name = f"{key}.{subkey}" if subkey is not None else key
            settings.extend(["-c", f"{name}={json.dumps(entry)}"])
    profile = {"read-only": ":read-only", "workspace-write": ":workspace"}[config["sandbox_mode"]]
    output = run([binary, *settings, "sandbox", "--permission-profile", profile,
                  "--cd", str(project), "--", sys.executable, "-c", PROBE, access], project)
    if "PASS: source=" not in output:
        raise RuntimeError("sandbox did not execute the write assertions: " + output)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="ai-1176-sandbox-") as directory:
        parent = Path(directory).resolve()
        for grant in ("signoff", "override"):
            run([sys.executable, "automation/init_project.py", grant, str(parent)], ROOT)
            project = parent / grant
            gatekeeper = [sys.executable, "automation/gatekeeper.py"]
            print(f"Fresh project: {grant}", flush=True)
            probe(args.codex, project, "read")
            if grant == "signoff":
                state = project / ".governance/gate_state.json"
                payload = json.loads(state.read_text())
                payload.update(approval_state="approved", implementation_authorized=True,
                               decision="Acceptance-test fixture sign-off")
                state.write_text(json.dumps(payload))
                env = {**os.environ, "FACTORY_OPERATOR_KEY_FILE": str(parent / "operator.key")}
                run([*gatekeeper, "init-operator-key"], project, env)
                run([*gatekeeper, "sign"], project, env)
            else:
                evidence = project / "docs/decisions/override.md"
                evidence.write_text("Acceptance-test fixture: temporary implementation authority.\n")
                now = datetime.now(timezone.utc)
                row = (f"| {(now - timedelta(minutes=1)).isoformat()} | implementation-override | "
                       "implementation_authorized=true | Test operator | Human Director: Test director | "
                       f"docs/decisions/override.md | {(now + timedelta(hours=1)).isoformat()} |\n")
                with (project / ".governance/security-compliance/override-register.md").open("a") as handle:
                    handle.write(row)
                run([sys.executable, "automation/codex_config.py", "codex-config"], project)
            probe(args.codex, project, "write")
    print("PASS: 4 sandbox phases (2 denied before authority, 2 allowed after authority)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as exc:
        print(f"FAIL: native Codex sandbox acceptance: {exc}", file=sys.stderr)
        sys.exit(1)
