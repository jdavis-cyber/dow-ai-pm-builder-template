"""AI-1177 / DEF-018: refuse DW-HITL-08 paths before dispatch."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from portable import portable_command  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    shutil.copytree(ROOT / "automation", root / "automation",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ROOT / ".gitignore", root / ".gitignore")
    for directory in ("orchestration", ".governance", "docs/verification", "subagents"):
        (root / directory).mkdir(parents=True)
    (root / ".governance/gate_state.json").write_text(json.dumps({
        "approval_state": "draft", "implementation_authorized": False,
    }), encoding="utf-8")
    shutil.copyfile(ROOT / "subagents/install-config.json", root / "subagents/install-config.json")
    monkeypatch.setenv("FACTORY_CHAIN_ANCHOR_DIR", str(tmp_path / "anchors"))
    monkeypatch.setenv("FACTORY_OPERATOR_KEY_FILE", str(tmp_path / "operator.key"))
    (tmp_path / "operator.key").write_text("k" * 64, encoding="utf-8")
    monkeypatch.setenv("FACTORY_ADAPTER_COMMAND", portable_command(*[
        sys.executable, "-c", "from pathlib import Path; Path('docs/dispatched').touch()",
    ]))
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def cli(project, script="governed_factory", *args):
    return subprocess.run([sys.executable, f"automation/{script}.py", *args],
                          cwd=project, text=True, capture_output=True, timeout=30)


def board(project, **changes):
    fields = {
        "Task ID": "TASK-901", "Phase": "Discovery", "Status": "Ready",
        "Owner Agent": "Requirements BA", "Required Inputs": "None",
        "Dependencies": "None", "Acceptance Criteria": "Record planning notes",
        "Evidence Required": "`docs/verification/notes.md`",
        "Verification Command or Method": "Review notes", "Handoff Target": "Scrum Master",
        "Gate Impact": "none", "Requires Authority": "none", "Human Gate": "no",
    }
    fields.update(changes)
    (project / "orchestration/tasks.md").write_text(
        "#### TASK-901: Planning notes\n" + "\n".join(
            f"**{key}**: {value}" for key, value in fields.items()) + "\n", encoding="utf-8")
    # Commit fixture setup so the real pre-dispatch dirty-tree audit can run.
    subprocess.run(["git", "add", "."], cwd=project, check=True)
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "commit", "-qm", "Synthetic dispatch fixture"], cwd=project, check=True)


def assert_refused(project, result, path):
    assert result.returncode == 2, result.stdout + result.stderr
    assert "REFUSAL:" in result.stdout
    assert path in result.stdout
    assert "implementation needs sign-off" in result.stdout
    assert not (project / "docs/dispatched").exists()
    runs = project / "docs/verification/factory-runs"
    records = list(runs.glob("*-result.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["task_id"] == "TASK-901"
    assert record["outcome"] == "refused: denied task paths"
    assert record["adapter_dispatched"] is False
    assert path in [item["path"] for item in record["checks"]["task_paths"]["denied"]]
    assert record["previous_result_sha256"] is None
    assert not list((runs / "pending-assisted").glob("*.json"))
    assert list(runs.glob("*.json")) == records  # no task packet was emitted


def test_dw_hitl_08_plain_source_path_is_refused_before_shell_dispatch(project):
    board(project, **{"Acceptance Criteria": "Record planning notes and create src/early.py"})
    result = cli(project, "governed_factory", "--adapter", "shell")
    assert_refused(project, result, "src/early.py")


def test_quoted_source_path_with_spaces_is_named_in_refusal(project):
    board(project, **{"Acceptance Criteria": 'Record notes and create "src/early draft.py"'})
    assert_refused(project, cli(project), "src/early draft.py")


@pytest.mark.parametrize("path", [
    "src/early.py", "services/api.py", "packages/lib.py", "database/schema.sql",
    "infrastructure/main.tf", "execution/run.sh", "src/", "`src`",
    "./src/early.py", "docs/../src/early.py",
])
def test_protected_paths_in_task_text_are_refused(project, path):
    board(project, **{"Required Inputs": path})
    assert_refused(project, cli(project), path.strip("`"))


@pytest.mark.parametrize("field", [
    "Evidence Required", "Plan", "Verification Command or Method", "Handoff Target",
])
def test_source_reference_in_any_task_field_is_refused(project, field):
    board(project, **{field: "src/early.py"})
    assert_refused(project, cli(project), "src/early.py")


def test_source_reference_in_unstructured_task_text_is_refused(project):
    board(project)
    task_file = project / "orchestration/tasks.md"
    task_file.write_text(task_file.read_text(encoding="utf-8") + "\nAlso create src/early.py.\n", encoding="utf-8")
    assert_refused(project, cli(project), "src/early.py")


@pytest.mark.parametrize("field,path", [
    ("Evidence Required", ".governance/gate_state.json"),
    ("Evidence Required", "automation/early.py"),
    ("Evidence Required", "`Makefile`"),
    ("Evidence Required", ".env"),
    ("Plan", ".governance/plan.md"),
])
def test_declared_outputs_use_gatekeeper_write_rules(project, field, path):
    board(project, **{field: path})
    assert_refused(project, cli(project), path.strip("`"))


def test_source_path_inside_quoted_prose_is_refused(project):
    board(project, **{"Acceptance Criteria": '"PM/PO asks for src/early.py"'})
    assert_refused(project, cli(project), "src/early.py")


@pytest.mark.parametrize("marker", ["**", "__", "*", "_", "***"])
def test_markdown_source_reference_is_refused(project, marker):
    board(project, **{"Acceptance Criteria": f"Create {marker}src/early.py{marker}"})
    assert_refused(project, cli(project), "src/early.py")


@pytest.mark.parametrize("field,value", [
    ("Plan", "Makefile"), ("Evidence Required", "Makefile"),
    ("Evidence Required", "Makefile; docs/notes.md"),
    ("Plan", "**Makefile**"),
])
def test_bare_declared_output_is_refused(project, field, value):
    board(project, **{"Human Gate": "yes", "Plan": "docs/plan.md", field: value})
    assert_refused(project, cli(project), "Makefile")


@pytest.mark.parametrize("script", ["governed_factory", "run_factory"])
def test_plan_only_and_legacy_entry_points_cannot_bypass_refusal(project, script):
    board(project, **{"Human Gate": "yes", "Plan": "docs/plan.md",
                      "Acceptance Criteria": "Record notes and create src/early.py"})
    assert_refused(project, cli(project, script), "src/early.py")


def test_existing_planning_task_with_read_only_references_still_dispatches(project):
    board(project, **{
        "Acceptance Criteria": "Discuss infrastructure, database, services, packages and execution",
        "Required Inputs": ".governance/Phase_Gates/Gate1_BusinessUnderstanding/",
        "Verification Command or Method":
            "python3 automation/validate_spec.py --mode locked orchestration/system_spec.md; "
            "python3 automation/validate_tasks.py orchestration/tasks.md",
    })
    result = cli(project, "run_factory")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "NEXT GOVERNED FACTORY TASK: TASK-901" in result.stdout
    runs = project / "docs/verification/factory-runs"
    assert not list(runs.glob("*-result.json"))
    assert (runs / "pending-assisted/TASK-901.json").exists()


@pytest.mark.parametrize("authority", ["signoff", "signed_override"])
def test_authorized_source_task_still_dispatches(project, monkeypatch, authority):
    state_file = project / ".governance/gate_state.json"
    if authority == "signoff":
        state_file.write_text(json.dumps({"approval_state": "approved",
                                          "implementation_authorized": True,
                                          "decision": "Synthetic Gate 1 sign-off"}), encoding="utf-8")
    else:
        now = datetime.now(timezone.utc)
        evidence = project / "docs/override.md"
        evidence.write_text("Synthetic source scope and rollback approval.\n", encoding="utf-8")
        register = project / ".governance/security-compliance/override-register.md"
        register.parent.mkdir(parents=True)
        register.write_text(
            "| " + " | ".join([(now - timedelta(minutes=1)).isoformat(),
            "implementation-override", "implementation_authorized=true", "Operator Example",
            "Human Director: Director Example", "docs/override.md",
            (now + timedelta(hours=1)).isoformat()]) + " |\n", encoding="utf-8")
    signed = cli(project, "gatekeeper", "sign")
    assert signed.returncode == 0, signed.stdout + signed.stderr
    board(project, **{"Acceptance Criteria": "Create src/early.py"})
    monkeypatch.setenv("FACTORY_ADAPTER_COMMAND", portable_command(*[sys.executable, "-c",
        "from pathlib import Path; Path('src').mkdir(exist_ok=True); "
        "Path('src/early.py').write_text('# synthetic source\\n'); "
        "Path('docs/verification/notes.md').write_text('Synthetic evidence\\n'); "
        "p=Path('orchestration/tasks.md'); "
        "p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))",
    ]))
    result = cli(project, "governed_factory", "--adapter", "shell")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "src/early.py").exists()
    records = list((project / "docs/verification/factory-runs").glob("*-result.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["outcome"] == "pass"
    assert record["gate_state_at_check"]["implementation_authorized"] is True



def test_evidence_annotation_is_not_a_declared_output():
    # "PM/PO" in an evidence note is prose, not a write destination.
    sys.path.insert(0, str(ROOT / "automation"))
    import governed_factory as gf

    task = {"Task ID": "TASK-901", "Acceptance Criteria": "Record planning notes",
            "Evidence Required": "`docs/verification/notes.md` — PM/PO review"}
    assert gf.denied_task_paths(task, {}) == []
    task["Evidence Required"] = "docs/verification/notes.md, automation/early.py — PM/PO review"
    assert [item["path"] for item in gf.denied_task_paths(task, {})] == ["automation/early.py"]
