#!/usr/bin/env python3
"""
Gatekeeper — the shared governance brain for ALL agent runtimes.

This single module is invoked from the PreToolUse / SessionStart / UserPromptSubmit
hooks of Claude Code, Gemini CLI, and Codex CLI, and from the automation layer
(run_factory.py). It is the one place that decides whether an action is permitted
given the canonical machine-readable gate state in .governance/gate_state.json.

Design: three independently-sufficient enforcement rings all call this brain, so the
decision logic never forks per runtime. Stdlib only.

Subcommands:
    hook --runtime {claude|gemini|codex}   Read a runtime hook event on stdin, decide,
                                            emit that runtime's allow/block response.
    check-action --tool T [--path P] [--command C]
                                            Pure decision (exit 0 allow / non-zero block).
    refresh-lock0                           Run spec validation, record result in state.
    status [--terse]                        Print current phase + gate status.
    session-banner                          Emit the SessionStart re-injection block.
    verify-consistency                      Verify every approval signature + JSON/markdown agreement.

Approval signatures use HMAC-SHA256. The signing helpers here are imported by
approve_gate.py so the canonical payload can never drift between signer and verifier.
"""

import argparse
import hashlib
import hmac
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# State/key paths are overridable via env so tests run hermetically against a copy.
STATE_PATH = pathlib.Path(os.environ.get("DOW_GATE_STATE", ROOT / ".governance" / "gate_state.json"))
KEY_FILE = pathlib.Path(os.environ.get("DOW_GATE_KEY_FILE", ROOT / ".governance" / ".gate_key"))
# Volatile runtime state (Lock 0 result + timestamp) lives in a SEPARATE, gitignored
# file so refreshing it never dirties the committed, durable gate_state.json.
RUNTIME_PATH = pathlib.Path(os.environ.get("DOW_GATE_RUNTIME", ROOT / ".governance" / "gate_runtime.json"))
SECRET_ENV = "DOW_GATE_SECRET"

# Gate is open only for these decisions (with a valid signature).
OPEN_DECISIONS = {"Approved", "Conditionally Approved"}

# Directory trees that constitute "building" and are gated (Director decision).
#
# Earlier template versions only protected execution/. That was too narrow for
# the single-repo operating model because many real project repos keep source in
# conventional locations such as src/, apps/, packages/, database/, or
# infrastructure/. The gatekeeper now protects both the template's legacy
# execution/ surface and common deployable-product surfaces.
GATED_WRITE_PREFIXES = (
    "execution/",
    "src/",
    "app/",
    "apps/",
    "packages/",
    "services/",
    "database/",
    "infrastructure/",
    ".github/workflows/",
)

# Root-level build/runtime manifests that can materially change the deployable
# product even when they are not located under a gated directory.
GATED_WRITE_FILES = (
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "Dockerfile",
    "Containerfile",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "go.mod",
    "go.sum",
    "pyproject.toml",
    "poetry.lock",
    "requirements.txt",
    "requirements-dev.txt",
)

# Discovery surfaces an agent may always write to, even with a closed gate.
# (Informational; anything not gated is allowed by default.)
DISCOVERY_PREFIXES = ("docs/", ".governance/", "memory/", "orchestration/tasks.md",
                      "directives/requirements/", "directives/stories/")

# The canonical state file may never be written by an agent tool call.
PROTECTED_PATHS = (".governance/gate_state.json",)

# Roles that produce code in execution/ (gated). Used by run_factory.py via import.
BUILDER_ROLES = {
    "backend-developer", "frontend-developer", "database-engineer",
    "pipeline-devops", "performance-devops", "automation-test-engineer",
}

# Bash patterns that indicate a filesystem mutation.
_BASH_MUTATION = re.compile(
    r"(>>?|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i\b|\bgit\s+add\b|\bgit\s+commit\b|\btruncate\b|\bdd\b)"
)

PHASE_NAMES = {
    "I": "Business Understanding", "II": "Data Understanding", "III": "Data Preparation",
    "IV": "Model Development", "V": "Model Evaluation", "VI": "Operationalization",
}

# Cross-runtime tool-name normalization. Each runtime names its tools differently;
# we map them to a small set of categories so the decision logic stays single-source.
_READ_TOOLS = {"read", "readfile", "read_file", "grep", "glob", "ls", "list_dir",
               "notebookread", "search_file_content", "cat", "view"}
_WRITE_TOOLS = {"write", "writefile", "write_file", "edit", "multiedit", "notebookedit",
                "replace", "edit_file", "create_file", "str_replace_editor",
                "str_replace_based_edit_tool"}
_BASH_TOOLS = {"bash", "shell", "run_shell_command", "exec_command", "local_shell",
               "execute", "runcommand", "run_command"}
_PATCH_TOOLS = {"apply_patch", "applypatch", "patch"}


def normalize_tool(tool):
    """Map any runtime's tool name to: read | write | bash | patch | other."""
    t = (tool or "").strip().lower()
    if t in _READ_TOOLS:
        return "read"
    if t in _WRITE_TOOLS:
        return "write"
    if t in _BASH_TOOLS:
        return "bash"
    if t in _PATCH_TOOLS:
        return "patch"
    return "other"


# --------------------------------------------------------------------------- state

def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    os.replace(tmp, STATE_PATH)


def active_gate(state):
    """Return (gate_id, gate_dict) for the current phase, or (None, None)."""
    phase = state.get("current_phase")
    for gid, gate in state.get("gates", {}).items():
        if gate.get("phase") == phase:
            return gid, gate
    return None, None


def load_runtime():
    """Volatile runtime state (Lock 0). Absent file => UNKNOWN (fail-closed)."""
    if RUNTIME_PATH.exists():
        try:
            return json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"lock0_spec_validation": {"status": "UNKNOWN", "last_checked_utc": None,
                                      "checked_by": None}}


def save_runtime(runtime):
    tmp = RUNTIME_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(runtime, f, indent=2)
        f.write("\n")
    os.replace(tmp, RUNTIME_PATH)


def lock0_status(state=None):
    """Current Lock 0 status: runtime file first, then the gate_state seed default."""
    status = load_runtime().get("lock0_spec_validation", {}).get("status")
    if status:
        return status
    if state is not None:
        return state.get("lock0_spec_validation", {}).get("status", "UNKNOWN")
    return "UNKNOWN"


def spec_path_for(state):
    return state.get("lock0_spec_validation", {}).get("spec_path",
                                                      "orchestration/system_spec.md")


# ------------------------------------------------------------------- signing core

def load_secret():
    """Resolve the Director signing secret. Returns bytes or None.

    Order: DOW_GATE_SECRET env var, then the gitignored key file. The key file must
    not be world/group-readable.
    """
    env = os.environ.get(SECRET_ENV)
    if env:
        return env.encode("utf-8")
    if KEY_FILE.exists():
        mode = KEY_FILE.stat().st_mode
        if mode & 0o077:
            sys.stderr.write(
                f"[gatekeeper] REFUSING to use {KEY_FILE}: permissions too open "
                f"(must be 600). Run: chmod 600 {KEY_FILE}\n")
            return None
        return KEY_FILE.read_text(encoding="utf-8").strip().encode("utf-8")
    return None


def canonical_payload(project, gate_id, gate_phase, approval):
    """Deterministic string the signature covers. Shared by signer and verifier."""
    fields = {
        "project": project,
        "gate_id": gate_id,
        "phase": gate_phase,
        "decision": approval.get("decision"),
        "approver_role": approval.get("approver_role"),
        "approver_name": approval.get("approver_name"),
        "approved_utc": approval.get("approved_utc"),
        "conditions": approval.get("conditions", ""),
        "key_id": approval.get("key_id"),
    }
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_signature(secret, payload_str):
    return hmac.new(secret, payload_str.encode("utf-8"), hashlib.sha256).hexdigest()


def approval_is_valid(state, gate_id, gate):
    """True iff the gate carries an approval whose HMAC verifies against the secret."""
    approval = gate.get("approval")
    if not approval or not approval.get("signature"):
        return False
    secret = load_secret()
    if secret is None:
        # No secret available => cannot verify => fail closed.
        return False
    payload = canonical_payload(state.get("project"), gate_id, gate.get("phase"), approval)
    expected = compute_signature(secret, payload)
    return hmac.compare_digest(expected, approval.get("signature", ""))


def gate_is_open(state, gate_id, gate):
    if gate is None:
        return False
    if gate.get("status") not in OPEN_DECISIONS:
        return False
    return approval_is_valid(state, gate_id, gate)


# ----------------------------------------------------------------- decision logic

class Decision:
    def __init__(self, allow, reason=""):
        self.allow = allow
        self.reason = reason


def _norm_path(path):
    """Strip a single leading './' prefix without touching leading dots of names."""
    p = path or ""
    while p.startswith("./"):
        p = p[2:]
    return p


def _is_gated_path(path):
    p = _norm_path(path)
    name = pathlib.PurePosixPath(p).name
    return (any(p.startswith(prefix) for prefix in GATED_WRITE_PREFIXES)
            or p in GATED_WRITE_FILES
            or name in GATED_WRITE_FILES)


def _is_protected_path(path):
    p = _norm_path(path)
    return any(p == prot or p.startswith(prot) for prot in PROTECTED_PATHS)


def _gated_write_decision(state, target):
    """Shared verdict for a write/mutation aimed at a concrete path."""
    if _is_protected_path(target):
        return Decision(False, "Writing .governance/gate_state.json is forbidden for agents. "
                               "Only the signed approve_gate.py changes gate state.")
    if _is_gated_path(target):
        gid, gate = active_gate(state)
        lock0 = lock0_status(state)
        if lock0 != "PASS":
            return Decision(False, f"Lock 0 (spec validation) is {lock0}. Resolve placeholders in "
                                   f"the system spec before writing to gated implementation paths.")
        if not gate_is_open(state, gid, gate):
            return Decision(False, _closed_reason(state, gid, gate, target))
    return Decision(True)


def evaluate(state, tool, path=None, command=None, blob=None):
    """Core allow/block decision. Reads are always allowed.

    `blob` is a best-effort concatenation of all stringy inputs, used to scan
    patch-/shell-style tools (e.g. Codex apply_patch) that embed target paths.
    """
    kind = normalize_tool(tool)

    if kind == "read" or kind == "other":
        # Reads and non-mutating tools (MCP queries, etc.) are always allowed.
        return Decision(True)

    if kind == "write":
        if path:
            return _gated_write_decision(state, path)
        # No explicit path: fall through to blob scan below.

    # bash / patch / write-without-path: scan command + blob for target markers.
    haystack = " ".join(x for x in (command, blob) if x)
    if kind == "bash" and not _BASH_MUTATION.search(haystack):
        return Decision(True)  # read-only shell
    if ".governance/gate_state.json" in haystack:
        return Decision(False, "Action targets the protected gate_state.json. "
                               "Only the signed approve_gate.py may change gate state.")
    if (any(prefix.rstrip("/") + "/" in haystack or haystack.strip().startswith(prefix)
            for prefix in GATED_WRITE_PREFIXES)
            or any(target in haystack for target in GATED_WRITE_FILES)):
        gid, gate = active_gate(state)
        lock0 = lock0_status(state)
        if lock0 != "PASS":
            return Decision(False, f"Lock 0 (spec validation) is {lock0}. Resolve placeholders in "
                                   f"the system spec before writing to gated implementation paths.")
        if not gate_is_open(state, gid, gate):
            return Decision(False, _closed_reason(state, gid, gate, "gated implementation paths"))
    return Decision(True)


def _closed_reason(state, gid, gate, target):
    status = gate.get("status") if gate else "Not Approved"
    phase = state.get("current_phase")
    return (f"BLOCKED: writing to {target} is not permitted while phase {phase} gate "
            f"'{gid}' is '{status}' (closed). Switch to discovery/documentation "
            f"(docs/, .governance/ narrative, memory/, tasks.md). A gate opens only via a "
            f"signed Director approval (automation/approve_gate.py); an agent's ceiling is "
            f"'READY FOR VERIFICATION'.")


# --------------------------------------------------------------- runtime adapters

def _collect_strings(obj, acc):
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _collect_strings(v, acc)


def _parse_hook_stdin():
    """Tolerantly extract (tool, path, command, blob) from any runtime's hook JSON."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return None, None, None, raw

    tool = (data.get("tool_name") or data.get("tool") or data.get("name")
            or data.get("toolName"))
    inp = (data.get("tool_input") or data.get("input") or data.get("args")
           or data.get("arguments") or {})
    if not isinstance(inp, dict):
        inp = {}
    path = (inp.get("file_path") or inp.get("path") or inp.get("filePath")
            or inp.get("filename") or inp.get("file"))
    command = inp.get("command") or inp.get("cmd")
    acc = []
    _collect_strings(inp, acc)
    blob = " ".join(acc)
    return tool, path, command, blob


def _emit_decision(runtime, decision):
    """Emit the allow/block response in the runtime's expected shape; set exit code."""
    if decision.allow:
        # Silence + exit 0 means "no objection" in all three runtimes.
        return 0

    reason = decision.reason
    if runtime == "claude":
        out = {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}
    elif runtime == "gemini":
        out = {"decision": "block", "reason": reason,
               "hookSpecificOutput": {"permissionDecision": "deny",
                                      "permissionDecisionReason": reason}}
    else:  # codex
        out = {"decision": "deny", "reason": reason,
               "permissionDecision": "deny", "permissionDecisionReason": reason}

    sys.stdout.write(json.dumps(out) + "\n")
    sys.stderr.write(reason + "\n")
    # Exit code 2 is the universal "block" signal across these runtimes.
    return 2


# --------------------------------------------------------------------- lock 0

def refresh_lock0(state=None):
    """Validate the spec and record the result in the gitignored RUNTIME file.

    Crucially this does NOT write gate_state.json, so a SessionStart refresh never
    dirties the committed, durable state. Returns the runtime dict.
    """
    import contextlib
    import datetime
    sys.path.insert(0, str(ROOT / "automation"))
    import validate_spec  # local import to keep hooks lightweight
    if state is None:
        state = load_state()
    spec_path = spec_path_for(state)
    abs_spec = ROOT / spec_path
    # validate_spec prints to stdout; redirect to stderr so it never pollutes a
    # captured prompt (run_factory) or a hook's stdout response.
    with contextlib.redirect_stdout(sys.stderr):
        ok = validate_spec.validate_spec(str(abs_spec))
    runtime = {
        "lock0_spec_validation": {
            "status": "PASS" if ok else "FAIL",
            "spec_path": spec_path,
            "last_checked_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "checked_by": "gatekeeper",
        }
    }
    save_runtime(runtime)
    return runtime


# --------------------------------------------------------------------- reporting

def status_text(state, terse=False):
    gid, gate = active_gate(state)
    phase = state.get("current_phase")
    gstatus = gate.get("status") if gate else "UNKNOWN"
    lock0 = lock0_status(state)
    open_ = gate_is_open(state, gid, gate)
    if terse:
        blk = "OPEN: implementation writes allowed" if open_ else "implementation writes BLOCKED"
        return f"GOVERNANCE: Phase {phase} | {gid} {gstatus} | {blk} | Lock0 {lock0}"
    name = PHASE_NAMES.get(phase, "")
    lines = [
        "=== GOVERNANCE STATE (machine-enforced) ===",
        f"Current CPMAI Phase: {phase} — {name}",
        f"Active Gate: {gid} — {gstatus}" + ("  (OPEN)" if open_ else "  (CLOSED)"),
        f"Lock 0 (spec validation): {lock0}",
        "Enforcement: PreToolUse hooks ACTIVE via automation/gatekeeper.py.",
        ("Writes to implementation paths are BLOCKED until this gate is Approved by a signed Director "
         "approval." if not open_ else "This gate is OPEN; implementation writes are permitted."),
        "You MAY: read anything; write discovery docs to docs/, .governance/ narrative, "
        "memory/, orchestration/tasks.md.",
        "You MAY NOT: edit .governance/gate_state.json (only the human-run approve_gate.py can).",
        "A preparing agent may set a gate to 'READY FOR VERIFICATION' only. It CANNOT self-approve.",
    ]
    return "\n".join(lines)


def verify_consistency(state):
    """Return list of problems (empty == consistent)."""
    problems = []
    for gid, gate in state.get("gates", {}).items():
        approval = gate.get("approval")
        status = gate.get("status")
        if status in OPEN_DECISIONS:
            if not approval:
                problems.append(f"{gid}: status '{status}' but no approval record (forgeable text).")
            elif not approval_is_valid(state, gid, gate):
                problems.append(f"{gid}: status '{status}' but signature INVALID/unverifiable "
                                f"=> treated as CLOSED.")
        if approval and approval.get("decision") != status and status in OPEN_DECISIONS:
            problems.append(f"{gid}: status '{status}' disagrees with approval.decision "
                            f"'{approval.get('decision')}'.")
    return problems


# ------------------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(prog="gatekeeper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_hook = sub.add_parser("hook")
    p_hook.add_argument("--runtime", choices=["claude", "gemini", "codex"], required=True)

    p_check = sub.add_parser("check-action")
    p_check.add_argument("--tool", required=True)
    p_check.add_argument("--path", default=None)
    p_check.add_argument("--command", default=None)

    sub.add_parser("refresh-lock0")

    p_status = sub.add_parser("status")
    p_status.add_argument("--terse", action="store_true")

    sub.add_parser("session-banner")
    sub.add_parser("verify-consistency")

    args = parser.parse_args(argv)

    if args.cmd == "hook":
        state = load_state()
        tool, path, command, blob = _parse_hook_stdin()
        decision = evaluate(state, tool, path, command, blob)
        return _emit_decision(args.runtime, decision)

    if args.cmd == "check-action":
        state = load_state()
        decision = evaluate(state, args.tool, args.path, args.command)
        if decision.allow:
            return 0
        sys.stderr.write(decision.reason + "\n")
        return 2

    if args.cmd == "refresh-lock0":
        refresh_lock0()
        print(status_text(load_state(), terse=True))
        return 0

    if args.cmd == "status":
        print(status_text(load_state(), terse=args.terse))
        return 0

    if args.cmd == "session-banner":
        print(status_text(load_state(), terse=False))
        return 0

    if args.cmd == "verify-consistency":
        problems = verify_consistency(load_state())
        if problems:
            sys.stderr.write("GATE STATE INCONSISTENT / FORGERY DETECTED:\n")
            for p in problems:
                sys.stderr.write("  - " + p + "\n")
            return 1
        print("Gate state consistent: all open gates carry valid signatures.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
