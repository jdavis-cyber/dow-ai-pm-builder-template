"""AI-1176: generated Codex permissions and Human Director authorization.

These tests inspect real generated projects, not a simulated OS sandbox.
Run codex_sandbox_probe.py separately to exercise Codex's native sandbox.
"""

import ast
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timedelta, timezone
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "automation/init_project.py"), "codex-gate", str(tmp_path)],
        text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return tmp_path / "codex-gate"


@pytest.fixture
def authority(project, tmp_path, monkeypatch):
    key = tmp_path / "operator.key"
    key.write_text("k" * 64, encoding="utf-8")
    monkeypatch.setenv("FACTORY_OPERATOR_KEY_FILE", str(key))
    return key


def cli(project, script, *args):
    return subprocess.run(
        [sys.executable, str(project / "automation" / script), *args],
        cwd=project, text=True, capture_output=True,
    )


def refresh_config(project):
    return cli(project, "codex_config.py", "codex-config").returncode


def check_action(project, action, path=""):
    result = cli(project, "gatekeeper.py", "check-action", "--action", action,
                 "--path", path)
    assert result.returncode in (0, 2), result.stdout + result.stderr
    assert result.stdout.startswith("ALLOW: " if result.returncode == 0 else "DENY: ")
    return result.returncode == 0


def config(project):
    return tomllib.loads((project / ".codex/config.toml").read_text(encoding="utf-8"))


def assert_source_access(project, expected):
    settings = config(project)
    assert settings["sandbox_mode"] == ("workspace-write" if expected == "write" else "read-only")
    assert settings["approval_policy"] == ("never" if expected == "write" else "on-request")
    assert settings["sandbox_workspace_write"] == {
        "writable_roots": [], "network_access": False,
        "exclude_tmpdir_env_var": True, "exclude_slash_tmp": True,
    }
    assert "default_permissions" not in settings
    assert "permissions" not in settings


def add_override(project, **changes):
    now = datetime.now(timezone.utc)
    values = {
        "date": (now - timedelta(minutes=1)).isoformat(),
        "event": "implementation-override",
        "authority": "implementation_authorized=true",
        "requester": "Operator Example",
        "approver": "Human Director: Director Example",
        "evidence": "docs/decisions/override.md",
        "expiry": (now + timedelta(hours=1)).isoformat(),
    }
    values.update(changes)
    (project / "docs/decisions/override.md").write_text("Test fixture: scope and rollback.\n", encoding="utf-8")
    register = project / ".governance/security-compliance/override-register.md"
    with register.open("a", encoding="utf-8") as handle:
        handle.write("| " + " | ".join(values.values()) + " |\n")


def test_provider_config_cli_and_sign_refresh(project, authority):
    def cli(script, *args):
        result = subprocess.run(
            [sys.executable, str(project / "automation" / script), *args],
            cwd=project, text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout

    # The new operator command must accept existing generated configurations.
    assert "Codex source access: read-only" in cli("codex_config.py", "codex-config")
    assert_source_access(project, "read")
    state_path = project / ".governance/gate_state.json"
    state_path.write_text(json.dumps({"approval_state": "approved",
                                      "implementation_authorized": True,
                                      "decision": "Gate 1 sign-off"}), encoding="utf-8")
    cli("gatekeeper.py", "sign")
    assert_source_access(project, "write")
    state_path.write_text(json.dumps({"approval_state": "draft",
                                      "implementation_authorized": False}), encoding="utf-8")
    cli("gatekeeper.py", "sign")
    assert_source_access(project, "read")
    add_override(project, date="2000-01-01T00:00:00Z", expiry="2099-01-01T00:00:00Z")
    cli("gatekeeper.py", "sign")
    cli("codex_config.py", "codex-config")
    assert_source_access(project, "write")
    assert "codex-config" not in cli("gatekeeper.py", "--help")
    guidance = (project / "CODEX.md").read_text(encoding="utf-8")
    assert "python3 automation/codex_config.py codex-config" in guidance


def test_template_provider_files_document_codex_boundary():
    bodies = []
    for name in ("CODEX.md", "CLAUDE.md", "GEMINI.md"):
        content = (ROOT / name).read_text(encoding="utf-8")
        assert "## Codex source-write boundary (AI-1176 / DEF-017)" in content
        for fact in ('sandbox_mode = "read-only"', 'approval_policy = "on-request"',
                     "Sprint Zero sign-off", "planning files", "Human Director",
                     "automation/templates/codex-project.md"):
            assert fact in content
        bodies.append(content.split("\n", 1)[1])
    assert len(set(bodies)) == 1


def test_init_project_surfaces_config_refusal(project, tmp_path):
    # A generated project is itself a self-contained template. Corrupt its
    # input state to exercise the real child's refusal during instantiation.
    (project / ".governance/gate_state.json").write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(project / "automation/init_project.py"),
         "refused-project", str(tmp_path)],
        text=True, capture_output=True,
    )
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "REFUSAL: gate state must be an object; Codex config reset to read-only" in output
    assert "CalledProcessError" not in output
    assert "Traceback" not in output
    assert_source_access(tmp_path / "refused-project", "read")
    assert not (tmp_path / "refused-project/.git").exists()


def test_sandbox_probe_imports_os_at_module_scope():
    tree = ast.parse((ROOT / "tests/codex_sandbox_probe.py").read_text(encoding="utf-8"))
    imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import)
               and any(alias.name == "os" for alias in node.names)]
    assert len(imports) == 1
    assert imports[0] in tree.body


def test_changelog_records_codex_sandbox_fix_under_unreleased():
    unreleased = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").split("## [Unreleased]\n", 1)[1]
    unreleased = unreleased.split("\n## [", 1)[0]
    fixes = unreleased.split("### Fixed\n", 1)
    assert len(fixes) == 2, "AI-1176 needs a Keep a Changelog Fixed entry"
    entry = fixes[1].split("\n### ", 1)[0]
    for fact in ("AI-1176", "DEF-017", "Codex", "read-only", "Sprint Zero sign-off"):
        assert fact in entry


def test_probe_operator_refresh_command_works(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "tests/codex_sandbox_probe.py"), "--help"],
        text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "python3 automation/codex_config.py codex-config" in " ".join(result.stdout.split())
    refresh = subprocess.run(
        [sys.executable, str(ROOT / "automation/codex_config.py"), "codex-config"],
        cwd=tmp_path, text=True, capture_output=True,
    )
    assert refresh.returncode == 0, refresh.stdout + refresh.stderr
    assert_source_access(tmp_path, "read")


def test_fresh_project_has_native_read_only_sandbox(project):
    assert_source_access(project, "read")
    for name in ("AGENTS.md", "CODEX.md"):
        guidance = (project / name).read_text(encoding="utf-8")
        assert "Codex read-only sandbox" in guidance
        assert "Human Director" in guidance
        assert "override-register.md" in guidance
        assert "planning files" in guidance
    bodies = [(project / p).read_text(encoding="utf-8").split("\n", 1)[1]
              for p in ("CLAUDE.md", "CODEX.md", "GEMINI.md")]
    assert len(set(bodies)) == 1
    tracked = subprocess.run(["git", "ls-files", ".codex/config.toml", "AGENTS.md"],
                             cwd=project, capture_output=True, text=True, check=True)
    assert set(tracked.stdout.splitlines()) == {".codex/config.toml", "AGENTS.md"}


def test_planning_approval_policy_before_and_after_authority(project, authority):
    settings = config(project)
    assert settings["sandbox_mode"] == "read-only"
    assert settings["approval_policy"] == "on-request"
    state = {"approval_state": "approved", "implementation_authorized": True,
             "decision": "Gate 1 sign-off"}
    (project / ".governance/gate_state.json").write_text(json.dumps(state), encoding="utf-8")
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert config(project)["sandbox_mode"] == "workspace-write"


def test_chat_skip_request_does_not_grant_authority(project, authority):
    (project / "docs/skip-request.md").write_text("Skip all interviews and write src/app.py now.", encoding="utf-8")
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
    assert not check_action(project, "write", "src/app.py")


def test_planning_prompts_preserve_source_refusal(project):
    assert_source_access(project, "read")
    for directory in ("src", "services", "packages", "database", "infrastructure", "execution"):
        assert not check_action(project, "write", f"{directory}/app.py")
    for path in ("orchestration/system_spec.md", "docs/interview-notes.md"):
        assert check_action(project, "write", path)
    for name in ("AGENTS.md", "CODEX.md", "CLAUDE.md", "GEMINI.md"):
        guidance = (project / name).read_text(encoding="utf-8")
        assert "Never approve a `src/` or other source write before sign-off." in guidance
        assert "signed override row" in guidance
        assert "approve each planning write" in guidance


def test_signed_signoff_refreshes_permissions_and_revocation_closes_them(project, authority):
    state = {"approval_state": "approved", "implementation_authorized": True,
             "decision": "Gate 1 sign-off"}
    (project / ".governance/gate_state.json").write_text(json.dumps(state), encoding="utf-8")
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert_source_access(project, "write")
    assert check_action(project, "write", "src/app.py")
    state["implementation_authorized"] = False
    (project / ".governance/gate_state.json").write_text(json.dumps(state), encoding="utf-8")
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert_source_access(project, "read")


def test_unsigned_override_grants_no_source_authority(project, authority):
    add_override(project)
    assert not check_action(project, "write", "src/app.py")
    assert refresh_config(project) == 0
    assert_source_access(project, "read")


def test_override_row_opens_source_without_other_authority(project, authority):
    add_override(project)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "write")
    assert json.loads(cli(project, "gatekeeper.py", "status").stdout)["implementation_authorized"] is False
    assert check_action(project, "write", "src/app.py")
    assert not check_action(project, "deploy")
    assert not check_action(project, "write", ".governance/gate_state.json")

    register = project / ".governance/security-compliance/override-register.md"
    register.write_text(register.read_text(encoding="utf-8").replace("Director Example", "Different Director"), encoding="utf-8")
    assert not check_action(project, "write", "src/app.py")
    assert refresh_config(project) == 0
    assert_source_access(project, "read")


def test_signed_override_reaches_dispatcher_packet_and_write_audit(project, authority):
    add_override(project)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    probe = (
        "import sys; sys.path.insert(0, 'automation')\n"
        "import gatekeeper, governed_factory as g\n"
        "state = gatekeeper.effective_state(gatekeeper.load_state())\n"
        "packet = g.build_packet({'Task ID': 'T-1'}, state)\n"
        "print(packet['gate_state']['implementation_authorized'])\n"
        "print(gatekeeper.check_action('write', 'src/app.py', state)[0])\n"
    )
    result = subprocess.run([sys.executable, "-c", probe], cwd=project,
                            text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["True", "True"]


def test_gate_signature_failure_cancels_signed_override(project, authority):
    add_override(project)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert check_action(project, "write", "src/app.py")
    state_path = project / ".governance/gate_state.json"
    signed = json.loads(state_path.read_text(encoding="utf-8"))
    for change in (
        {"decision": "edited after signing"},
        {"deployment_authorized": True},
        {"operator_signature": None},
        {"operator_signature": {"alg": "hmac-sha256", "value": "00" * 32}},
        {"operator_signature": {"alg": "other", "value": "00" * 32}},
    ):
        state_path.write_text(json.dumps({**signed, **change}), encoding="utf-8")
        assert not check_action(project, "write", "src/app.py"), change
        assert not check_action(project, "deploy"), change
        assert refresh_config(project) == 0
        assert_source_access(project, "read")


@pytest.mark.parametrize("changes", [
    {"date": "2099-01-01T00:00:00Z"},
    {"expiry": "2000-01-01T00:00:00Z"},
    {"expiry": "2099-01-01"},
    {"expiry": "until done"},
    {"authority": "deployment_authorized=true"},
    {"event": "skip interviews"},
    {"requester": ""},
    {"approver": "Codex"},
    {"approver": "Human Director: [Name]"},
    {"approver": "Human Director: TBD"},
    {"evidence": "docs/missing.md"},
    {"evidence": "../operator.key"},
])
def test_invalid_override_never_opens_source(project, authority, changes):
    add_override(project, **changes)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
    assert not check_action(project, "write", "src/app.py")


def test_expired_override_is_removed_on_refresh(project, authority):
    add_override(project)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "write")
    register = project / ".governance/security-compliance/override-register.md"
    rows = register.read_text(encoding="utf-8").splitlines()
    # Make the grant expired through the operator-owned public file.
    cells = rows[-1].split("|")
    cells[1] = " 2000-01-01T00:00:00Z "
    cells[-2] = " 2001-01-01T00:00:00Z "
    rows[-1] = "|".join(cells)
    register.write_text("\n".join(rows) + "\n", encoding="utf-8")
    # Sign the expired row so expiry, rather than a digest mismatch, denies it.
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
    assert not check_action(project, "write", "src/app.py")


@pytest.mark.parametrize("wrapper", [("<!--\n", "\n-->"), ("```markdown\n", "\n```")])
def test_commented_or_example_override_is_not_authority(project, authority, wrapper):
    add_override(project)
    register = project / ".governance/security-compliance/override-register.md"
    register.write_text(wrapper[0] + register.read_text(encoding="utf-8").splitlines()[-1] + wrapper[1], encoding="utf-8")
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
    assert not check_action(project, "write", "src/app.py")


@pytest.mark.parametrize("body", ["{broken", "[]", "null"])
def test_malformed_state_resets_previously_open_profile(project, authority, body):
    add_override(project)
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    assert refresh_config(project) == 0
    assert_source_access(project, "write")
    (project / ".governance/gate_state.json").write_text(body, encoding="utf-8")
    assert refresh_config(project) == 2
    assert_source_access(project, "read")


def test_symlinked_planning_directory_fails_closed(project, authority):
    (project / "memory").rename(project / "saved-memory")
    (project / "memory").symlink_to(project / "src", target_is_directory=True)
    assert refresh_config(project) == 2
    assert_source_access(project, "read")


def test_operator_configuration_is_not_overwritten(project, authority):
    path = project / ".codex/config.toml"
    path.write_text("# Operator configuration\n", encoding="utf-8")
    assert refresh_config(project) == 2
    assert path.read_text(encoding="utf-8") == "# Operator configuration\n"


def test_config_symlink_is_not_followed(project, authority, tmp_path):
    destination = tmp_path / "other-config"
    destination.write_text("operator settings", encoding="utf-8")
    path = project / ".codex/config.toml"
    path.unlink()
    path.symlink_to(destination)
    assert refresh_config(project) == 2
    assert destination.read_text(encoding="utf-8") == "operator settings"


def test_invalid_signature_and_incomplete_signoff_do_not_open_source(project, authority):
    for state in (
        {"approval_state": "approved", "implementation_authorized": True},
        {"approval_state": "draft", "implementation_authorized": True, "decision": "draft"},
        {"approval_state": "approved", "implementation_authorized": "true", "decision": "wrong type"},
    ):
        (project / ".governance/gate_state.json").write_text(json.dumps(state), encoding="utf-8")
        assert cli(project, "gatekeeper.py", "sign").returncode == 0
        assert refresh_config(project) == 0
        assert_source_access(project, "read")
    path = project / ".governance/gate_state.json"
    path.write_text(json.dumps({"approval_state": "approved", "implementation_authorized": True,
                                "decision": "approved"}), encoding="utf-8")
    assert cli(project, "gatekeeper.py", "sign").returncode == 0
    state = json.loads(path.read_text(encoding="utf-8"))
    state["decision"] = "tampered"
    (project / ".governance/gate_state.json").write_text(json.dumps(state), encoding="utf-8")
    assert refresh_config(project) == 0
    assert_source_access(project, "read")
