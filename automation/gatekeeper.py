#!/usr/bin/env python3
"""Provider-neutral gate and authority checks for governed factory runs.

This module intentionally knows nothing about Claude, Codex, Gemini, Hermes, or
any other model runtime. It answers one question for the factory dispatcher:
"Is this action legal under the current project governance state?"
"""

from __future__ import annotations

import argparse
import json
import sys
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
PLANNING_PREFIXES = (
    "docs/",
    ".governance/",
    "orchestration/",
    "directives/",
    "requirements/",
    "memory/",
    "PROJECT.md",
    "README.md",
    "KICKOFF.md",
)


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


def is_protected_source_path(path: str) -> bool:
    rp = rel(path)
    return any(rp == prefix.rstrip("/") or rp.startswith(prefix) for prefix in PROTECTED_SOURCE_PREFIXES)


def check_action(action: str, path: str | None = None, state: dict | None = None) -> tuple[bool, str]:
    state = state or load_state()
    action = action.lower().strip()
    path = path or ""

    if action in {"read", "inspect", "validate", "plan"}:
        return True, "read/inspect/validate/plan actions are allowed"

    if action in {"write", "edit", "create"}:
        if path and is_protected_source_path(path) and not state.get("implementation_authorized", False):
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
    if errors:
        for e in errors:
            print("CONSISTENCY ERROR: " + e)
        return 2
    print("gatekeeper consistency check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral governance gatekeeper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("verify-consistency")
    chk = sub.add_parser("check-action")
    chk.add_argument("--action", required=True)
    chk.add_argument("--path", default="")
    args = parser.parse_args(argv)

    if args.cmd == "status":
        return status()
    if args.cmd == "verify-consistency":
        return verify_consistency()
    if args.cmd == "check-action":
        ok, msg = check_action(args.action, args.path)
        print(("ALLOW: " if ok else "DENY: ") + msg)
        return 0 if ok else 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
