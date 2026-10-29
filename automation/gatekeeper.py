#!/usr/bin/env python3
"""Provider-neutral gate and authority checks for governed factory runs.

Authority decisions are independent of model runtimes. Provider-specific
configuration lives in separate modules; sign refreshes existing configuration.
This module answers one question for the factory dispatcher:
"Is this action legal under the current project governance state?"
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
GATE_STATE = ROOT / ".governance" / "gate_state.json"
PROTECTED_SOURCE_PREFIXES = (
    "src/",
    "services/",
    "packages/",
    "database/",
    "infrastructure/",
    "execution/",
)
# Authority records are written by the human operator only. No agent action may
# write them, whatever the current authorization state, and the post-dispatch
# audit flags any adapter change here.
AUTHORITY_PREFIXES = (
    ".governance/",
)
PLANNING_PREFIXES = (
    "docs/",
    "orchestration/",
    "directives/",
    "requirements/",
    "memory/",
    "PROJECT.md",
    "README.md",
    "KICKOFF.md",
)
AUTHORITY_FLAGS = (
    "implementation_authorized",
    "source_admission_authorized",
    "external_tracker_writes_authorized",
    "deployment_authorized",
    "real_data_or_api_authorized",
    "cdrl_submission_authorized",
    "risk_acceptance_authorized",
    "control_closure_authorized",
)
SIGNATURE_FIELD = "operator_signature"
OPERATOR_KEY_ENV = "FACTORY_OPERATOR_KEY_FILE"
OVERRIDE_REGISTER = Path(".governance/security-compliance/override-register.md")


def parse_iso8601(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, accepting the UTC Z suffix."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def implementation_override(state: dict) -> bool:
    """Recognize an operator-signed, unexpired Human Director row."""
    if not state.get("override_register_sha256") or not state.get(SIGNATURE_FIELD) or signature_error(state):
        return False
    try:
        content_bytes = (ROOT / OVERRIDE_REGISTER).read_bytes()
        if hashlib.sha256(content_bytes).hexdigest() != state["override_register_sha256"]:
            return False
        content = content_bytes.decode("utf-8")
    except (OSError, UnicodeError):
        return False
    now = datetime.now(timezone.utc)
    content = re.sub(r"<!--.*?(?:-->|$)", "", content, flags=re.DOTALL)
    fence = ""
    for row in content.splitlines():
        stripped = row.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not fence:
                fence = marker
            elif marker == fence:
                fence = ""
            continue
        if fence:
            continue
        if not row.strip().startswith("|") or not row.strip().endswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in row.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        date, event, authority, requester, approver, evidence, expiry = cells
        if event != "implementation-override" or authority != "implementation_authorized=true":
            continue
        if not requester or not approver.startswith("Human Director: "):
            continue
        name = approver.removeprefix("Human Director: ").strip()
        if any(not value or value.lower() in {"tbd", "todo", "pending", "n/a"}
               or "[" in value or "<" in value for value in (requester, name, evidence)):
            continue
        try:
            created = parse_iso8601(date)
            expires = parse_iso8601(expiry)
            if created.tzinfo is None or expires.tzinfo is None or not created <= now < expires:
                continue
            evidence_path = (ROOT / evidence).resolve()
            evidence_path.relative_to(ROOT.resolve())
            if not evidence_path.is_file() or not evidence_path.stat().st_size:
                continue
        except (ValueError, OSError):
            continue
        return True
    return False


def implementation_permission(state: dict) -> bool:
    """Verified sign-off or a Human Director override grants source access."""
    if signature_error(state):
        return False
    signed_off = (
        state.get("implementation_authorized") is True
        and state.get("approval_state") == "approved"
        and bool(state.get("decision") or state.get("decision_record"))
    )
    return signed_off or implementation_override(state)


def operator_key_path() -> Path:
    """Where the operator's signing key lives. It must be outside the project."""
    override = os.environ.get(OPERATOR_KEY_ENV, "").strip()
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "dow-factory" / "operator.key"


def _inside_project(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def _read_operator_key() -> tuple[bytes | None, str]:
    path = operator_key_path()
    if _inside_project(path):
        return None, f"operator key {path} is inside the project; it must live outside the agent's write set"
    try:
        key = path.read_bytes().strip()
    except OSError:
        return None, f"operator key {path} is unavailable"
    if len(key) < 32:
        return None, f"operator key {path} is too short"
    return key, ""


def _signed_payload(state: dict) -> bytes:
    body = {k: v for k, v in state.items() if k != SIGNATURE_FIELD}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sign_state(state: dict, key: bytes) -> dict:
    signed = {k: v for k, v in state.items() if k != SIGNATURE_FIELD}
    signed[SIGNATURE_FIELD] = {
        "alg": "hmac-sha256",
        "value": hmac.new(key, _signed_payload(signed), hashlib.sha256).hexdigest(),
    }
    return signed


def grants_authority(state: dict) -> bool:
    return str(state.get("approval_state", "")).lower() == "approved" or any(
        bool(state.get(flag)) for flag in AUTHORITY_FLAGS)


def signature_error(state: dict) -> str:
    """Verify signed drafts too: they can carry an implementation override."""
    if not grants_authority(state) and SIGNATURE_FIELD not in state and "override_register_sha256" not in state:
        return ""
    sig = state.get(SIGNATURE_FIELD)
    if not isinstance(sig, dict) or sig.get("alg") != "hmac-sha256" or not sig.get("value"):
        return "gate state grants authority without an operator signature; run `gatekeeper.py sign` as the operator"
    key, problem = _read_operator_key()
    if key is None:
        return "cannot verify operator signature: " + problem
    expected = hmac.new(key, _signed_payload(state), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(sig.get("value"))):
        return "operator signature does not match the gate state; the state was changed after signing"
    return ""


def plan_approval_path(task_id: str) -> Path:
    return ROOT / ".governance" / "plan-approvals" / f"{task_id}.json"


def plan_approval_error(task_id: str, plan_path: str) -> str:
    """Empty when the operator signed an approval of this exact plan."""
    path = plan_approval_path(task_id)
    try:
        record = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return f"no operator plan approval for {task_id}; run `gatekeeper.py approve-plan {task_id} <plan>`"
    plan_file = ROOT / plan_path
    try:
        digest = hashlib.sha256(plan_file.read_bytes()).hexdigest()
    except OSError:
        return f"plan {plan_path} for {task_id} is missing"
    if record.get("task_id") != task_id or record.get("plan") != plan_path or record.get("plan_sha256") != digest:
        return f"plan {plan_path} changed after it was approved, or the approval is for another task"
    key, problem = _read_operator_key()
    if key is None:
        return "cannot verify plan approval: " + problem
    sig = record.get(SIGNATURE_FIELD) or {}
    expected = hmac.new(key, _signed_payload(record), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, str(sig.get("value", ""))):
        return f"plan approval for {task_id} is not signed by the operator"
    return ""


def approve_plan(task_id: str, plan_path: str) -> int:
    """Operator command: approve the plan a Human Gate task wrote."""
    key, problem = _read_operator_key()
    if key is None:
        print("REFUSAL: " + problem + "; run `gatekeeper.py init-operator-key` first")
        return 2
    plan_file = ROOT / plan_path
    if not plan_file.is_file() or not plan_file.read_bytes().strip():
        print(f"REFUSAL: plan {plan_path} is missing or empty")
        return 2
    record = sign_state({
        "task_id": task_id,
        "plan": plan_path,
        "plan_sha256": hashlib.sha256(plan_file.read_bytes()).hexdigest(),
    }, key)
    plan_approval_path(task_id).parent.mkdir(parents=True, exist_ok=True)
    plan_approval_path(task_id).write_text(json.dumps(record, indent=2) + "\n")
    print(f"plan approved for {task_id}: {plan_path}; set the task status to Plan Approved")
    return 0


def load_state() -> dict:
    if not GATE_STATE.exists():
        return {
            "approval_state": "draft",
            "current_phase": "Sprint Zero / Phase 0",
            "implementation_authorized": False,
            "source_admission_authorized": False,
            "external_tracker_writes_authorized": False,
            "deployment_authorized": False,
            "real_data_or_api_authorized": False,
            "cdrl_submission_authorized": False,
            "risk_acceptance_authorized": False,
            "control_closure_authorized": False,
        }
    return json.loads(GATE_STATE.read_text())


def rel(path: str) -> str:
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return path.replace("\\", "/")


def is_planning_path(path: str) -> bool:
    rp = rel(path)
    return any(rp == prefix.rstrip("/") or rp.startswith(prefix) for prefix in PLANNING_PREFIXES)


def is_authority_path(path: str) -> bool:
    rp = rel(path)
    return any(rp == prefix.rstrip("/") or rp.startswith(prefix) for prefix in AUTHORITY_PREFIXES)


def is_protected_source_path(path: str) -> bool:
    rp = rel(path)
    return any(rp == prefix.rstrip("/") or rp.startswith(prefix) for prefix in PROTECTED_SOURCE_PREFIXES)


def paths_in_text(text: str) -> list[str]:
    """Extract path-shaped references without inferring intent from keywords."""
    paths = set()
    tokens = re.finditer(r'''`([^`\n]+)`|"([^"\n]+)"|'([^'\n]+)'|([^\s`"'<>()[\]{},;:=]+)''', text)
    for match in tokens:
        token = next(value for value in match.groups() if value is not None)
        quoted = match.group(4) is None
        # Keep quoted paths with spaces whole, but still inspect quoted prose
        # or commands such as "write src/app.py" for embedded paths.
        if quoted and len(token.split()) > 1:
            embedded = paths_in_text(token)
            if "/" not in token.split()[0].replace("\\", "/"):
                paths.update(embedded)
                continue
            paths.update(path for path in embedded if is_protected_source_path(path))
        path = token.replace("\\", "/").rstrip(".!?")
        while len(path) > 2 and path[0] in "*_" and path[-1] == path[0]:
            path = path[1:-1]
            quoted = True
        if quoted or "/" in path or re.fullmatch(r"(?:[\w.-]+\.[\w-]+|\.[\w-]+)", path):
            paths.add(path)
    return sorted(paths)


def effective_state(state: dict) -> dict:
    """Gate state with implementation_authorized set to the effective authority.

    A signed Human Director override grants source access while the stored
    flag stays false; every caller (selection, packets, write audit) must see
    the same answer. A bad signature yields an empty, unauthorized state.
    """
    implementation_allowed = implementation_permission(state)
    if signature_error(state):
        state = {}
    return {**state, "implementation_authorized": implementation_allowed}


def check_action(action: str, path: str | None = None, state: dict | None = None) -> tuple[bool, str]:
    if state is None:
        state = effective_state(load_state())
    action = action.lower().strip()
    path = path or ""

    if action in {"read", "inspect", "validate", "plan"}:
        return True, "read/inspect/validate/plan actions are allowed"

    if action in {"write", "edit", "create"}:
        if path and is_authority_path(path):
            return False, f"write to governance authority record {rel(path)} blocked; only the operator changes authority"
        if path and is_protected_source_path(path):
            if state.get("implementation_authorized", False):
                return True, f"implementation/source write allowed for {rel(path)}; implementation_authorized is true"
            return False, f"implementation/source write blocked for {rel(path)}; implementation_authorized is false"
        if path and is_planning_path(path):
            return True, f"planning/governance write allowed for {rel(path)}"
        return False, f"write target {rel(path) if path else '<unspecified>'} is not clearly planning/governance scope; fail closed"

    if action in {"admit-source", "source-admission"}:
        return (bool(state.get("source_admission_authorized", False)), "source admission authority required")

    if action in {"external-write", "tracker-write", "issue-import"}:
        return (bool(state.get("external_tracker_writes_authorized", False)), "external tracker write/import authority required")

    if action == "deploy":
        return (bool(state.get("deployment_authorized", False)), "deployment authority required")

    if action in {"real-data", "api-operation", "real-api"}:
        return (bool(state.get("real_data_or_api_authorized", False)), "real data/API operation authority required")

    if action in {"cdrl-submit", "cdrl-complete"}:
        return (bool(state.get("cdrl_submission_authorized", False)), "CDRL completion/submission authority required")

    if action == "risk-accept":
        return (bool(state.get("risk_acceptance_authorized", False)), "risk acceptance authority required")

    if action == "control-close":
        return (bool(state.get("control_closure_authorized", False)), "control closure authority required")

    return False, f"unknown action {action}; fail closed"


def status() -> int:
    state = load_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def verify_consistency() -> int:
    state = load_state()
    errors: list[str] = []
    approval = str(state.get("approval_state", "")).lower()
    if approval == "approved" and not (state.get("decision") or state.get("decision_record")):
        errors.append("approved gate state requires decision and/or decision_record")
    if state.get("implementation_authorized") and approval != "approved":
        errors.append("implementation_authorized cannot be true unless approval_state is approved")
    for key in [
        "source_admission_authorized",
        "external_tracker_writes_authorized",
        "deployment_authorized",
        "real_data_or_api_authorized",
        "cdrl_submission_authorized",
        "risk_acceptance_authorized",
        "control_closure_authorized",
    ]:
        if state.get(key) and not state.get("implementation_authorized", False) and key not in {"external_tracker_writes_authorized"}:
            errors.append(f"{key} is true while implementation_authorized is false; confirm this is intentional")
    problem = signature_error(state)
    if problem:
        errors.append(problem)
    if errors:
        for e in errors:
            print("CONSISTENCY ERROR: " + e)
        return 2
    print("gatekeeper consistency check passed")
    return 0


def init_operator_key() -> int:
    path = operator_key_path()
    if _inside_project(path):
        print(f"REFUSAL: operator key {path} must live outside the project")
        return 2
    if path.exists():
        print(f"operator key already exists: {path}")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(secrets.token_hex(32) + "\n")
    print(f"operator key created: {path}")
    return 0


def sign() -> int:
    """Operator command: sign the reviewed gate state and override register."""
    key, problem = _read_operator_key()
    if key is None:
        print("REFUSAL: " + problem + "; run `gatekeeper.py init-operator-key` first")
        return 2
    state = load_state()
    try:
        digest = hashlib.sha256((ROOT / OVERRIDE_REGISTER).read_bytes()).hexdigest()
    except FileNotFoundError:
        digest = None
    except OSError as exc:
        print(f"REFUSAL: cannot read override register: {exc}")
        return 2
    state["override_register_sha256"] = digest
    signed = sign_state(state, key)
    GATE_STATE.parent.mkdir(parents=True, exist_ok=True)
    GATE_STATE.write_text(json.dumps(signed, indent=2, ensure_ascii=False) + "\n")
    print(f"gate state signed: {GATE_STATE.relative_to(ROOT)}")
    from codex_config import refresh_if_present

    return refresh_if_present()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral governance gatekeeper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("verify-consistency")
    sub.add_parser("init-operator-key", help="operator: create the signing key outside the project")
    sub.add_parser("sign", help="operator: sign the reviewed gate state and override register")
    ap = sub.add_parser("approve-plan", help="operator: approve a Human Gate task's written plan")
    ap.add_argument("task_id")
    ap.add_argument("plan")
    chk = sub.add_parser("check-action")
    chk.add_argument("--action", required=True)
    chk.add_argument("--path", default="")
    args = parser.parse_args(argv)

    if args.cmd == "status":
        return status()
    if args.cmd == "verify-consistency":
        return verify_consistency()
    if args.cmd == "init-operator-key":
        return init_operator_key()
    if args.cmd == "sign":
        return sign()
    if args.cmd == "approve-plan":
        return approve_plan(args.task_id, args.plan)
    if args.cmd == "check-action":
        ok, msg = check_action(args.action, args.path)
        print(("ALLOW: " if ok else "DENY: ") + msg)
        return 0 if ok else 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
