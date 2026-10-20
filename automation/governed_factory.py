#!/usr/bin/env python3
"""Provider-neutral governed factory dispatcher.

The dispatcher owns governance, task selection, stop conditions, and evidence
expectations. Provider-specific model execution lives behind adapters. The
factory can therefore run with Claude, Codex, Gemini, OpenCode, Hermes, a local
runner, or assisted mode without changing governance rules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import gatekeeper

ROOT = Path.cwd()
TASKS_FILE = ROOT / "orchestration" / "tasks.md"
LOG_DIR = ROOT / "docs" / "verification" / "factory-runs"
CHAIN_HEAD = "chain/head.json"  # kept apart from the per-run records
CONFIG_FILES = ("factory.config.json", "factory.config.example.json")
# Every stop condition is mandatory: stop_on documents them and the dispatcher
# refuses a config that drops one or names one it does not implement.
MANDATORY_STOPS = (
    "human_input_required",
    "phase_gate_readiness",
    "authority_boundary",
    "validation_failure",
    "dirty_unexpected_state",
    "missing_evidence",
)
DEFAULT_LIMITS = {
    "max_iterations": 20,
    "max_wall_seconds": 7200,
    "adapter_timeout_seconds": 1800,
    "max_tokens": None,
    "max_cost_usd": None,
}
OUTPUT_TAIL_CHARS = 20000
CHAIN_ANCHOR_ENV = "FACTORY_CHAIN_ANCHOR_DIR"
# Credential shapes scrubbed from anything copied into a run record.
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(bearer|token|authorization)(\s*[:=]\s*|\s+)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)\b([A-Z0-9_]*(?:API_KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*)=\S+"),
    re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"(?<=://)[^/\s:@]+:[^/\s@]+(?=@)"),
)
ADAPTER_TIMEOUT_EXIT = 124

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
    "advances gate",
    "blocks gate",
)


def load_factory_config() -> dict:
    """The ``factory`` section of the local config, else of the shipped example."""
    for name in CONFIG_FILES:
        path = ROOT / name
        if path.is_file():
            return (json.loads(path.read_text()).get("factory") or {})
    return {}


def factory_limits(cfg: dict) -> dict:
    limits = dict(DEFAULT_LIMITS)
    limits.update({k: v for k, v in (cfg.get("limits") or {}).items() if k in DEFAULT_LIMITS})
    return limits


def config_problems(cfg: dict) -> list[str]:
    problems: list[str] = []
    stop_on = cfg.get("stop_on", list(MANDATORY_STOPS))
    if not isinstance(stop_on, list):
        return ["factory.stop_on must be a list"]
    for name in MANDATORY_STOPS:
        if name not in stop_on:
            problems.append(f"factory.stop_on cannot drop mandatory stop {name}")
    for name in stop_on:
        if name not in MANDATORY_STOPS:
            problems.append(f"factory.stop_on names unknown stop {name}")
    for key, value in factory_limits(cfg).items():
        if value is None and key in {"max_tokens", "max_cost_usd"}:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            problems.append(f"factory.limits.{key} must be a positive number")
    return problems


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


def redact(text: str) -> str:
    """Scrub credential-shaped strings before they reach a persisted record."""
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _tail(text: str) -> str:
    return redact(text[-OUTPUT_TAIL_CHARS:])


def _run_adapter(command: str, prompt: str, env: dict, timeout: float) -> tuple[int, str, str, bool]:
    """Run the adapter in its own process group so a timeout stops all of it."""
    proc = subprocess.Popen(command, shell=True, cwd=ROOT, env=env, text=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = proc.communicate(prompt, timeout=timeout)
        return proc.returncode, out, err, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
        out, err = proc.communicate()
        return ADAPTER_TIMEOUT_EXIT, out, err, True


def dispatch(packet: dict, adapter: str, run_info: dict | None = None) -> int:
    adapter = adapter.lower().strip()
    run_info = {} if run_info is None else run_info
    cfg = load_factory_config()
    prompt = packet_to_prompt(packet)
    default_record = "true" if cfg.get("record_packets_by_default", True) else "false"
    record_packets = os.environ.get("FACTORY_RECORD_PACKETS", default_record).lower() == "true"
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
        usage_path = packet_path.with_name(packet_path.stem + "-usage.json")
        env = os.environ.copy()
        env["FACTORY_TASK_PACKET"] = str(packet_path)
        env["FACTORY_TASK_PROMPT"] = prompt
        env["FACTORY_USAGE_FILE"] = str(usage_path)
        timeout = factory_limits(cfg)["adapter_timeout_seconds"]
        code, out, err, timed_out = _run_adapter(command, prompt, env, timeout)
        sys.stdout.write(out)
        sys.stderr.write(err)
        run_info.update({
            "adapter_command": redact(command),
            "model_id": os.environ.get("FACTORY_MODEL_ID", "").strip() or "unreported",
            "provider_version": os.environ.get("FACTORY_PROVIDER_VERSION", "").strip() or "unreported",
            "adapter_stdout_tail": _tail(out),
            "adapter_stderr_tail": _tail(err),
            "adapter_output_sha256": hashlib.sha256((out + "\0" + err).encode()).hexdigest(),
            "adapter_timed_out": timed_out,
            "usage": _read_usage(usage_path),
        })
        if timed_out:
            print(f"STOP: adapter exceeded {timeout}s and was stopped")
        return code
    print(f"REFUSAL: unknown adapter {adapter}; use assisted or shell")
    return 2


def _read_usage(path: Path) -> dict | None:
    """Usage the adapter reported in FACTORY_USAGE_FILE: {"tokens": n, "cost_usd": x}."""
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    usage = {}
    for key in ("tokens", "cost_usd"):
        value = data.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
            usage[key] = value
    return usage or None


def _porcelain_paths(raw: bytes) -> set[str]:
    """Paths from ``git status --porcelain=v1 -z``.

    A rename or copy entry is ``XY new\0old\0``; both sides are returned so a
    ``git mv`` into a protected tree is seen at its destination.
    """
    fields = raw.decode("utf-8", "surrogateescape").split("\0")
    paths: set[str] = set()
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        paths.add(entry[3:])
        if entry[0] in "RC" or entry[1] in "RC":
            if i < len(fields) and fields[i]:
                paths.add(fields[i])
            i += 1
    return paths


def working_tree_changes() -> set[str] | None:
    """Paths currently dirty per git. None when the audit is unavailable."""
    r = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        return None
    return _porcelain_paths(r.stdout)


def _fingerprint(path: str) -> str | None:
    try:
        return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    except OSError:
        return None


def working_tree_snapshot() -> dict[str, str | None] | None:
    """Dirty paths and their content digests, so pre-existing dirt can't mask
    an adapter's later change to the same file. None when git is unusable."""
    changes = working_tree_changes()
    if changes is None:
        return None
    return {path: _fingerprint(path) for path in changes}


def evidence_paths(task: dict) -> list[str]:
    field = str(task.get("Evidence Required", ""))
    return [tok.strip() for tok in re.findall(r"`([^`]+)`", field) if "/" in tok]


def missing_evidence(task: dict) -> list[str]:
    """Declared evidence that is absent or has no content."""
    missing = []
    for p in evidence_paths(task):
        path = ROOT / p
        try:
            empty = path.is_file() and not path.read_bytes().strip()
        except OSError:
            empty = True
        if not path.exists() or empty:
            missing.append(p)
    return missing


def evidence_fingerprints(task: dict) -> dict[str, str | None]:
    return {p: _fingerprint(p) for p in evidence_paths(task)}


def chain_anchor_path() -> Path:
    """Operator-side copy of the chain head, outside the agent's write set."""
    base = os.environ.get(CHAIN_ANCHOR_ENV, "").strip()
    root = Path(base).expanduser() if base else Path.home() / ".config" / "dow-factory" / "chains"
    return root / (hashlib.sha256(str(ROOT.resolve()).encode()).hexdigest()[:24] + ".json")


def _chain_records() -> list[Path]:
    return sorted(LOG_DIR.glob("*-result.json")) if LOG_DIR.is_dir() else []


def verify_run_chain() -> list[str]:
    """Problems with the hash-chained run results; empty when intact.

    Each chained result names the SHA-256 of the result before it, and the head
    file names the latest. Deleting or editing any chained result breaks a link.
    Results written before chaining existed are accepted only before the first
    chained one.
    """
    problems: list[str] = []
    previous: tuple[str, str] | None = None
    chained = False
    for path in _chain_records():
        raw = path.read_bytes()
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            problems.append(f"{path.name}: not valid JSON")
            previous = (path.name, hashlib.sha256(raw).hexdigest())
            continue
        if "previous_result_sha256" in record:
            expected = previous[1] if previous else None
            if record["previous_result_sha256"] != expected:
                problems.append(f"{path.name}: chain link does not match the preceding result")
            chained = True
        elif chained:
            problems.append(f"{path.name}: unchained result after the chain started")
        previous = (path.name, hashlib.sha256(raw).hexdigest())
    head_path = LOG_DIR / CHAIN_HEAD
    if chained or head_path.exists():
        try:
            head = json.loads(head_path.read_text())
        except (OSError, json.JSONDecodeError):
            problems.append(f"{CHAIN_HEAD} missing or unreadable")
        else:
            latest = previous[0] if previous else None
            if head.get("latest_result") != latest:
                problems.append(f"{CHAIN_HEAD}: latest result {head.get('latest_result')} is not the newest record (deleted?)")
            elif previous and head.get("latest_result_sha256") != previous[1]:
                problems.append(f"{previous[0]}: content changed after it was recorded")
    try:
        anchor = json.loads(chain_anchor_path().read_text())
    except FileNotFoundError:
        anchor = None
    except (OSError, json.JSONDecodeError):
        problems.append(f"chain anchor {chain_anchor_path()} unreadable")
        anchor = None
    if anchor is not None:
        latest = previous[0] if previous else None
        latest_sha = previous[1] if previous else None
        if (anchor.get("latest_result"), anchor.get("latest_result_sha256")) != (latest, latest_sha):
            problems.append("run results do not match the operator-side chain anchor "
                            f"(expected {anchor.get('latest_result')}); records were removed or replaced")
    return problems


def adapter_changes(before, after) -> set[str]:
    """Paths the adapter run changed.

    New dirty paths always count. When ``before`` is a snapshot with content
    digests, a path that was already dirty counts too if its content changed.
    """
    changed = set(after) - set(before)
    if isinstance(before, dict):
        changed |= {p for p in set(after) & set(before) if _fingerprint(p) != before[p]}
    return changed


def unauthorized_writes(before, after, state: dict) -> list[str]:
    """Adapter-changed paths the gatekeeper would not allow it to write.

    Authority records are flagged whatever the authorization state; protected
    source is flagged unless implementation is authorized; anything outside
    planning scope is flagged (the gatekeeper fails closed on it).
    """
    return sorted(p for p in adapter_changes(before, after)
                  if not gatekeeper.check_action("write", p, state)[0])


def write_run_result(task: dict, result: dict) -> Path:
    """Persist the factory's own compliance record for this dispatch.

    Every autonomous run leaves a machine-readable result artifact — pass or
    violation — so the factory's governed operation is verifiable from the
    evidence trail, not from console output.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    prior = _chain_records()
    result = dict(result)
    result["previous_result_sha256"] = (
        hashlib.sha256(prior[-1].read_bytes()).hexdigest() if prior else None)
    path = LOG_DIR / f"{now_id()}-{task['Task ID']}-result.json"
    while path.exists() or (prior and path.name <= prior[-1].name):
        time.sleep(1)
        path = LOG_DIR / f"{now_id()}-{task['Task ID']}-result.json"
    raw = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode()
    path.write_bytes(raw)
    head = json.dumps({
        "latest_result": path.name,
        "latest_result_sha256": hashlib.sha256(raw).hexdigest(),
    }, indent=2) + "\n"
    (LOG_DIR / CHAIN_HEAD).parent.mkdir(exist_ok=True)
    (LOG_DIR / CHAIN_HEAD).write_text(head)
    anchor = chain_anchor_path()
    anchor.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    anchor.write_text(head)
    return path


# Usage reported by adapters across one dispatcher process (one --loop run).
USAGE_TOTALS = {"tokens": 0, "cost_usd": 0.0}


def post_dispatch_checks(task: dict, state: dict, before,
                         adapter_returncode: int = 0,
                         evidence_before: dict | None = None,
                         run_info: dict | None = None) -> int:
    """Record every adapter outcome and all applicable detective checks.

    A nonzero adapter exit retains its exit code and primary failure outcome.
    Simultaneous detective violations are recorded without masking that failure.
    For a successful adapter, the first detective violation retains exit code 3.
    """
    result = {
        "record_type": "factory-run-result",
        "task_id": task["Task ID"],
        "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gate_state_at_check": {k: state.get(k) for k in ["approval_state", "implementation_authorized", "deployment_authorized"]},
        "checks": {},
        "outcome": "pass",
        "adapter_returncode": adapter_returncode,
        "violations": [],
    }
    result.update(run_info or {})
    code = 0

    def violation(kind: str) -> None:
        nonlocal code
        result["violations"].append(kind)
        if code == 0:
            result["outcome"] = "violation: " + kind
        code = 3

    after = working_tree_changes()
    if before is None or after is None:
        print("STOP: post-run write audit unavailable (git not usable here); a control that cannot run does not pass")
        result["checks"]["write_audit"] = "fail: git unavailable"
        violation("write audit unavailable")
    else:
        viol = unauthorized_writes(before, after, state)
        result["checks"]["write_audit"] = {"violations": viol} if viol else "pass"
        if viol:
            print("STOP: unauthorized writes detected after dispatch: " + ", ".join(viol))
            violation("unauthorized writes")
    trail = verify_run_chain()
    if trail:
        result["checks"]["evidence_trail"] = {"problems": trail}
        print("STOP: earlier run results were changed or removed during dispatch: " + "; ".join(trail))
        violation("evidence trail modified")
    declared = evidence_paths(task)
    if not declared:
        result["checks"]["evidence_declared"] = "fail: Evidence Required names no paths"
        print(f"STOP: {task['Task ID']} declares no evidence paths; a run cannot pass against nothing.")
        violation("no evidence declared")
    missing = missing_evidence(task)
    result["checks"]["evidence_exists"] = {"missing": missing} if missing else "pass"
    if missing:
        print(f"STOP: required evidence missing or empty after dispatch for {task['Task ID']}: " + ", ".join(missing))
        violation("missing evidence")
    result["evidence_sha256"] = {p: _fingerprint(p) for p in declared}
    if evidence_before is not None and declared and not missing:
        unchanged = all(evidence_before.get(p) == result["evidence_sha256"][p] for p in declared)
        result["checks"]["evidence_changed"] = "fail: no evidence changed" if unchanged else "pass"
        if unchanged:
            print(f"STOP: {task['Task ID']} changed status but produced no new evidence.")
            violation("evidence unchanged")
    refreshed = {t["Task ID"]: t for t in parse_tasks(TASKS_FILE.read_text())}
    still_open = status_kind(refreshed.get(task["Task ID"], {}).get("Status", "")) == "open"
    result["checks"]["status_transitioned"] = "pass" if not still_open else "fail: task still open"
    if still_open:
        print(f"STOP: {task['Task ID']} is still open after dispatch; halting to prevent a redispatch loop. The adapter must update task status and evidence.")
        violation("no status transition")
    usage = (run_info or {}).get("usage")
    limits = factory_limits(load_factory_config())
    # Adapter-reported usage is self-attested; the dispatcher-enforced
    # max_iterations / max_wall_seconds / adapter timeout remain the hard bound.
    capped = [k for k, cap in (("tokens", limits["max_tokens"]), ("cost_usd", limits["max_cost_usd"])) if cap is not None]
    if capped:
        if usage is None or any(k not in usage for k in capped):
            result["checks"]["budget"] = "fail: adapter reported no usage"
            print("STOP: a spend ceiling is configured but the adapter reported no usage; human review required.")
            violation("budget unverifiable")
        else:
            USAGE_TOTALS["tokens"] += usage.get("tokens", 0)
            USAGE_TOTALS["cost_usd"] += usage.get("cost_usd", 0.0)
            over = [k for k, cap in (("tokens", limits["max_tokens"]), ("cost_usd", limits["max_cost_usd"]))
                    if cap is not None and USAGE_TOTALS[k] >= cap]
            result["checks"]["budget"] = {"totals": dict(USAGE_TOTALS), "exceeded": over} if over else "pass"
            if over:
                print("STOP: spend ceiling reached (" + ", ".join(over) + "); human review required before more runs.")
                violation("budget ceiling reached")
    if adapter_returncode != 0:
        print(f"STOP: adapter failed with exit code {adapter_returncode}; detective checks and failure evidence retained.")
        result["violations"].append("adapter failure")
        result["outcome"] = "violation: adapter failure"
        code = adapter_returncode
    if code != 0:
        print("Fail-closed halt. Any exception requires explicit human authorization recorded in "
              ".governance/security-compliance/override-register.md; this message grants no override or authority.")
    path = write_run_result(task, result)
    print(f"factory run result recorded: {path.relative_to(ROOT)}")
    return code


def once(adapter: str) -> int:
    if not TASKS_FILE.exists():
        print(f"REFUSAL: missing task board {TASKS_FILE}")
        return 2
    problems = config_problems(load_factory_config())
    if problems:
        for problem in problems:
            print("REFUSAL: " + problem)
        return 2
    consistency = gatekeeper.verify_consistency()
    if consistency != 0:
        return consistency
    chain = verify_run_chain()
    if chain:
        for problem in chain:
            print("STOP: evidence trail broken: " + problem)
        return 2
    tasks = parse_tasks(TASKS_FILE.read_text())
    task, reason = select_next_task(tasks)
    if not task:
        print(reason)
        return 0 if reason.startswith("STOP: no ready") else 2
    state = gatekeeper.load_state()
    packet = build_packet(task, state)
    if adapter.lower().strip() == "shell":
        before = working_tree_snapshot()
        if before is not None:
            dirty = sorted(p for p in before if not gatekeeper.check_action("write", p, state)[0])
            if dirty:
                print("STOP: dirty_unexpected_state: uncommitted changes outside the agent's write scope: "
                      + ", ".join(dirty))
                return 2
        evidence_before = evidence_fingerprints(task)
        run_info: dict = {}
        code = dispatch(packet, adapter, run_info)
        return post_dispatch_checks(task, state, before, adapter_returncode=code,
                                    evidence_before=evidence_before, run_info=run_info)
    return dispatch(packet, adapter)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral governed factory dispatcher")
    parser.add_argument("--adapter", default=os.environ.get("FACTORY_ADAPTER", "assisted"), help="assisted or shell")
    parser.add_argument("--loop", action="store_true", help="continue until no ready task or a stop/refusal occurs")
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--max-iterations", type=int, default=None,
                        help="stop the loop after this many dispatches (default from factory config)")
    parser.add_argument("--max-wall-seconds", type=int, default=None,
                        help="stop the loop after this much wall-clock time (default from factory config)")
    args = parser.parse_args(argv)
    limits = factory_limits(load_factory_config())
    max_iterations = args.max_iterations or limits["max_iterations"]
    max_wall = args.max_wall_seconds or limits["max_wall_seconds"]
    started = time.monotonic()
    iterations = 0
    while True:
        code = once(args.adapter)
        iterations += 1
        if not args.loop or code != 0:
            return code
        if iterations >= max_iterations:
            print(f"STOP: loop reached {iterations} dispatches (max_iterations); human review required to continue")
            return 4
        if time.monotonic() - started >= max_wall:
            print(f"STOP: loop ran {int(time.monotonic() - started)}s (max_wall_seconds); human review required to continue")
            return 4
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
