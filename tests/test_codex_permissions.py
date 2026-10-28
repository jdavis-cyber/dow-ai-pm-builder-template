"""AI-1176: generated Codex permissions and Human Director authorization.

These tests inspect real generated projects, not a simulated OS sandbox.
Run codex_sandbox_probe.py separately to exercise Codex's native sandbox.
"""

import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timedelta, timezone
import tomllib
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))
import gatekeeper


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
    key.write_text("k" * 64)
    monkeypatch.setattr(gatekeeper, "ROOT", project)
    monkeypatch.setattr(gatekeeper, "GATE_STATE", project / ".governance/gate_state.json")
    monkeypatch.setenv(gatekeeper.OPERATOR_KEY_ENV, str(key))
    return key


def config(project):
    return tomllib.loads((project / ".codex/config.toml").read_text())


def assert_source_access(project, expected):
    settings = config(project)
    assert settings["sandbox_mode"] == ("workspace-write" if expected == "write" else "read-only")
    assert settings["approval_policy"] == "never"
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
    (project / "docs/decisions/override.md").write_text("Test fixture: scope and rollback.\n")
    register = project / ".governance/security-compliance/override-register.md"
    with register.open("a") as handle:
        handle.write("| " + " | ".join(values.values()) + " |\n")


def test_fresh_project_has_native_read_only_sandbox(project):
    assert_source_access(project, "read")
    for name in ("AGENTS.md", "CODEX.md"):
        guidance = (project / name).read_text()
        assert "Codex read-only sandbox" in guidance
        assert "Human Director" in guidance
        assert "override-register.md" in guidance
        assert "planning files" in guidance
    bodies = [(project / p).read_text().split("\n", 1)[1]
              for p in ("CLAUDE.md", "CODEX.md", "GEMINI.md")]
    assert len(set(bodies)) == 1
    tracked = subprocess.run(["git", "ls-files", ".codex/config.toml", "AGENTS.md"],
                             cwd=project, capture_output=True, text=True, check=True)
    assert set(tracked.stdout.splitlines()) == {".codex/config.toml", "AGENTS.md"}


def test_chat_skip_request_does_not_grant_authority(project, authority):
    (project / "docs/skip-request.md").write_text("Skip all interviews and write src/app.py now.")
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")
    assert not gatekeeper.check_action("write", str(project / "src/app.py"))[0]


def test_signed_signoff_refreshes_permissions_and_revocation_closes_them(project, authority):
    state = {"approval_state": "approved", "implementation_authorized": True,
             "decision": "Gate 1 sign-off"}
    gatekeeper.GATE_STATE.write_text(json.dumps(state))
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")
    assert gatekeeper.sign() == 0
    assert_source_access(project, "write")
    assert gatekeeper.check_action("write", str(project / "src/app.py"))[0]
    state["implementation_authorized"] = False
    gatekeeper.GATE_STATE.write_text(json.dumps(state))
    assert gatekeeper.sign() == 0
    assert_source_access(project, "read")


def test_override_row_opens_source_without_other_authority(project, authority):
    add_override(project)
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "write")
    assert gatekeeper.load_state()["implementation_authorized"] is False
    assert gatekeeper.check_action("write", str(project / "src/app.py"))[0]
    assert not gatekeeper.check_action("deploy")[0]
    assert not gatekeeper.check_action("write", str(project / ".governance/gate_state.json"))[0]


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
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")


def test_expired_override_is_removed_on_refresh(project, authority):
    add_override(project)
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "write")
    with patch.object(gatekeeper, "datetime") as clock:
        clock.now.return_value = datetime.now(timezone.utc) + timedelta(days=1)
        clock.fromisoformat.side_effect = datetime.fromisoformat
        assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")


@pytest.mark.parametrize("wrapper", [("<!--\n", "\n-->"), ("```markdown\n", "\n```")])
def test_commented_or_example_override_is_not_authority(project, authority, wrapper):
    add_override(project)
    register = project / ".governance/security-compliance/override-register.md"
    register.write_text(wrapper[0] + register.read_text().splitlines()[-1] + wrapper[1])
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")


@pytest.mark.parametrize("body", ["{broken", "[]", "null"])
def test_malformed_state_resets_previously_open_profile(project, authority, body):
    add_override(project)
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "write")
    gatekeeper.GATE_STATE.write_text(body)
    assert gatekeeper.codex_config() == 2
    assert_source_access(project, "read")


def test_symlinked_planning_directory_fails_closed(project, authority):
    (project / "memory").rename(project / "saved-memory")
    (project / "memory").symlink_to(project / "src", target_is_directory=True)
    assert gatekeeper.codex_config() == 2
    assert_source_access(project, "read")


def test_operator_configuration_is_not_overwritten(project, authority):
    path = project / ".codex/config.toml"
    path.write_text("# Operator configuration\n")
    assert gatekeeper.codex_config() == 2
    assert path.read_text() == "# Operator configuration\n"


def test_config_symlink_is_not_followed(project, authority, tmp_path):
    destination = tmp_path / "other-config"
    destination.write_text("operator settings")
    path = project / ".codex/config.toml"
    path.unlink()
    path.symlink_to(destination)
    assert gatekeeper.codex_config() == 2
    assert destination.read_text() == "operator settings"


def test_invalid_signature_and_incomplete_signoff_do_not_open_source(project, authority):
    for state in (
        {"approval_state": "approved", "implementation_authorized": True},
        {"approval_state": "draft", "implementation_authorized": True, "decision": "draft"},
        {"approval_state": "approved", "implementation_authorized": "true", "decision": "wrong type"},
    ):
        gatekeeper.GATE_STATE.write_text(json.dumps(gatekeeper.sign_state(state, authority.read_bytes())))
        assert gatekeeper.codex_config() == 0
        assert_source_access(project, "read")
    state = gatekeeper.sign_state({"approval_state": "approved", "implementation_authorized": True,
                                  "decision": "approved"}, authority.read_bytes())
    state["decision"] = "tampered"
    gatekeeper.GATE_STATE.write_text(json.dumps(state))
    assert gatekeeper.codex_config() == 0
    assert_source_access(project, "read")
