#!/usr/bin/env python3
"""Provider-neutral governed factory dispatcher.

The dispatcher owns governance, task selection, stop conditions, and evidence
expectations. Provider-specific model execution lives behind adapters. The
factory can therefore run with Claude, Codex, Gemini, OpenCode, Hermes, a local
runner, or assisted mode without changing governance rules.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import gatekeeper

ROOT = Path.cwd()
TASKS_FILE = ROOT / "orchestration" / "tasks.md"
LOG_DIR = ROOT / "docs" / "verification" / "factory-runs"

ACCOUNTABLE = {
    "Requirements BA",
    "User Story BA",
    "UI/UX Designer",
    "Architecture SE",
    "Database Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Pipeline DevOps",
    "Performance DevOps",
    "QA Engineer",
    "Automation Test Engineer",
    "Scrum Master",
    "Program Analyst",
    "Documentation SE",
    "Security & Compliance Officer",
}
FIELDS = [
    "Task ID",
    "Phase",
    "Status",
    "Owner Agent",
    "Required Inputs",
    "Dependencies",
    "Acceptance Criteria",
    "Evidence Required",
    "Verification Command or Method",
    "Handoff Target",
    "Gate Impact",
]
COMPLETE_PREFIXES = ("done", "complete", "completed", "approved")
OPEN_PREFIXES = ("ready", "ready to start", "backlog", "pending")
HUMAN_STOP_PATTERNS = (
    "pm/po decision",
    "human authorization",
    "explicit approval",
    "phase gate",
    "gate decision",
    "director input",
)


def now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_tasks(text: str) -> list[dict]:
    chunks = re.split(r"(?=^####\s+)", text, flags=re.M)
    tasks: list[dict] = []
    for c in chunks:
        m = re.match(r"####\s+([^:\n]+):?\s*(.*)", c)
        if not m:
            continue
        task = {"Task ID": m.group(1).strip(), "Title": m.group(2).strip(), "raw": c}
        for f in FIELDS:
            mm = re.search(rf"\*\*{re.escape(f)}\*\*:\s*(.*)", c)
            if mm:
                task[f] = mm.group(1).strip()
        tasks.append(task)
    return tasks


def status_kind(status: str) -> str:
    s = status.strip().lower()
    if s.startswith(COMPLETE_PREFIXES):
        return "complete"
    if s.startswith(OPEN_PREFIXES) or "ready to start" in s:
        return "open"
    if "awaiting" in s or "blocked" in s or "hold" in s:
        return "blocked"
    return "unknown"


def deps_complete(task: dict, tasks: list[dict]) -> tuple[bool, list[str]]:
    deps = task.get("Dependencies", "None")
    if deps.lower() in {"none", "n/a", ""}:
        return True, []
    ids = re.findall(r"TASK-\d+", deps)
    by_id = {t["Task ID"]: t for t in tasks}
    missing = [d for d in ids if status_kind(by_id.get(d, {}).get("Status", "")) != "complete"]
    return not missing, missing


def task_needs_human(task: dict) -> bool:
    haystack = "\n".join(str(task.get(k, "")) for k in ["Title", "Status", "Acceptance Criteria", "Gate Impact", "Handoff Target"]).lower()
    return any(p in haystack for p in HUMAN_STOP_PATTERNS) and "planning only" not in haystack


def infer_required_actions(task: dict) -> list[tuple[str, str]]:
    text = "\n".join(str(task.get(k, "")) for k in ["Phase", "Title", "Acceptance Criteria", "Evidence Required", "Gate Impact"]).lower()
    actions: list[tuple[str, str]] = [("plan", "orchestration/tasks.md")]
    if any(word in text for word in ["implementation", "source write", "runtime write", "application source"]):
        if "does not authorize implementation" not in text and "no implementation" not in text:
            actions.append(("write", "src/"))
    if "external tracker" in text or "linear" in text or "jira" in text:
        if "no external" not in text and "does not authorize" not in text:
            actions.append(("external-write", ""))
    if "deploy" in text or "hosted preview" in text:
        if "no deployment" not in text and "does not authorize" not in text:
            actions.append(("deploy", ""))
    if "cdrl submission" in text or "cdrl completion" in text:
        if "no cdrl" not in text and "does not authorize" not in text:
            actions.append(("cdrl-submit", ""))
    return actions


def select_next_task(tasks: list[dict]) -> tuple[dict | None, str]:
    for task in tasks:
        kind = status_kind(task.get("Status", ""))
        if kind != "open":
            continue
        owner = task.get("Owner Agent", "Unassigned").strip().strip("[]")
        if owner not in ACCOUNTABLE:
            return None, f"REFUSAL: unknown accountable owner for {task['Task ID']}: {owner}"
        ok, missing = deps_complete(task, tasks)
        if not ok:
            return None, f"STOP: dependencies incomplete for {task['Task ID']}: {', '.join(missing)}"
        if task_needs_human(task):
            return None, f"STOP: {task['Task ID']} appears to require human/PM/PO/gate input"
        for action, path in infer_required_actions(task):
            allowed, msg = gatekeeper.check_action(action, path)
            if not allowed:
                return None, "STOP: " + msg
        return task, "selected"
    return None, "STOP: no ready tasks found"


def build_packet(task: dict, state: dict) -> dict:
    return {
        "packet_version": "1.0",
        "factory_contract": "provider-neutral-governed-task",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(ROOT),
        "gate_state": {
            "approval_state": state.get("approval_state", "draft"),
            "current_phase": state.get("current_phase", state.get("next_allowed_phase", "unknown")),
            "implementation_authorized": bool(state.get("implementation_authorized", False)),
            "source_admission_authorized": bool(state.get("source_admission_authorized", False)),
            "external_tracker_writes_authorized": bool(state.get("external_tracker_writes_authorized", False)),
            "deployment_authorized": bool(state.get("deployment_authorized", False)),
        },
        "task": {k: task.get(k, "") for k in ["Task ID", "Title", *FIELDS]},
        "required_actions_checked": infer_required_actions(task),
        "non_authorities": [
            "Do not perform implementation/source writes unless implementation_authorized is true.",
            "Do not admit prior prototype/source unless source_admission_authorized is true.",
            "Do not write/import external tracker issues unless external_tracker_writes_authorized is true.",
            "Do not deploy, use real data/APIs, submit CDRLs, accept risk, or close controls without explicit authority.",
        ],
        "expected_agent_behavior": [
            "Read startup/governance files before acting.",
            "Execute only the selected task scope.",
            "Create/update required evidence artifacts.",
            "Run task verification commands.",
            "Stop and report if human input, missing evidence, authority ambiguity, or validation failure appears.",
        ],
    }


def packet_to_prompt(packet: dict) -> str:
    task = packet["task"]
    lines = [
        f"NEXT GOVERNED FACTORY TASK: {task.get('Task ID')} - {task.get('Title')}",
        f"Owner Agent: {task.get('Owner Agent')}",
        f"Phase: {task.get('Phase')}",
        f"Status: {task.get('Status')}",
        f"Current Gate/Phase State: {json.dumps(packet['gate_state'], ensure_ascii=False)}",
        f"Required Inputs: {task.get('Required Inputs')}",
        f"Acceptance Criteria: {task.get('Acceptance Criteria')}",
        f"Evidence Required: {task.get('Evidence Required')}",
        f"Verification Command or Method: {task.get('Verification Command or Method')}",
        f"Handoff Target: {task.get('Handoff Target')}",
        "",
        "Provider-neutral factory contract:",
    ]
    lines.extend(f"- {x}" for x in packet["expected_agent_behavior"])
    lines.append("")
    lines.append("Non-authorities:")
    lines.extend(f"- {x}" for x in packet["non_authorities"])
    return "\n".join(lines)


def write_packet(packet: dict) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{now_id()}-{packet['task']['Task ID']}.json"
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n")
    return path


def dispatch(packet: dict, adapter: str) -> int:
    adapter = adapter.lower().strip()
    prompt = packet_to_prompt(packet)
    record_packets = os.environ.get("FACTORY_RECORD_PACKETS", "false").lower() == "true"
    packet_path = write_packet(packet) if record_packets else None
    if adapter == "assisted":
        print(prompt)
        if packet_path:
            print(f"\nASSISTED MODE: task packet written to {packet_path}")
        else:
            print("\nASSISTED MODE: no files changed. Set FACTORY_RECORD_PACKETS=true to save the task packet as evidence.")
        print("Configure --adapter shell with FACTORY_ADAPTER_COMMAND, or a provider-specific wrapper, for autonomous execution.")
        return 0
    if adapter == "shell":
        command = os.environ.get("FACTORY_ADAPTER_COMMAND", "").strip()
        if not command:
            print("REFUSAL: shell adapter requires FACTORY_ADAPTER_COMMAND")
            return 2
        if not packet_path:
            packet_path = write_packet(packet)
        env = os.environ.copy()
        env["FACTORY_TASK_PACKET"] = str(packet_path)
        env["FACTORY_TASK_PROMPT"] = prompt
        result = subprocess.run(command, input=prompt, text=True, shell=True, cwd=ROOT, env=env)
        return result.returncode
    print(f"REFUSAL: unknown adapter {adapter}; use assisted or shell")
    return 2


def once(adapter: str) -> int:
    if not TASKS_FILE.exists():
        print(f"REFUSAL: missing task board {TASKS_FILE}")
        return 2
    consistency = gatekeeper.verify_consistency()
    if consistency != 0:
        return consistency
    tasks = parse_tasks(TASKS_FILE.read_text())
    task, reason = select_next_task(tasks)
    if not task:
        print(reason)
        return 0 if reason.startswith("STOP: no ready") else 2
    packet = build_packet(task, gatekeeper.load_state())
    return dispatch(packet, adapter)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral governed factory dispatcher")
    parser.add_argument("--adapter", default=os.environ.get("FACTORY_ADAPTER", "assisted"), help="assisted or shell")
    parser.add_argument("--loop", action="store_true", help="continue until no ready task or a stop/refusal occurs")
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args(argv)
    while True:
        code = once(args.adapter)
        if not args.loop or code != 0:
            return code
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
