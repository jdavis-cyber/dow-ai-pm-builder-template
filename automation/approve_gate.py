#!/usr/bin/env python3
"""
approve_gate.py — the Director's signed approval ritual.

This is the ONLY channel that can move a phase gate to an "open" status
(Approved / Conditionally Approved). It is run OUT OF BAND by the human Director
and must never be handed to an agent as a task. It signs the gate decision with
an HMAC-SHA256 secret that lives only on the Director's machine (env var or a
gitignored key file), so no agent — which has no legitimate access to the secret
and cannot write gate_state.json through its hooked tools — can forge an approval.

A preparing agent's maximum power is `mark-ready` (status: READY FOR VERIFICATION).

Usage:
    python3 automation/approve_gate.py init-key
    python3 automation/approve_gate.py approve \
        --gate Gate1_BusinessUnderstanding --decision "Approved" \
        --approver-role "Executive Sponsor" --approver-name "Jane Director" \
        [--conditions "SEC-39 verification complete"]
    python3 automation/approve_gate.py mark-ready --gate Gate1_BusinessUnderstanding \
        --by "scrum-master"

Stdlib only.
"""

import argparse
import datetime
import os
import pathlib
import secrets
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gatekeeper as gk  # shared state + signing helpers (single source of truth)

VALID_DECISIONS = {"Approved", "Conditionally Approved", "Not Approved"}


def _now():
    return datetime.datetime.utcnow().isoformat() + "Z"


def cmd_init_key():
    if gk.KEY_FILE.exists():
        sys.stderr.write(f"Key already exists at {gk.KEY_FILE}. Refusing to overwrite.\n")
        return 1
    gk.KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_hex(32)
    # Write then tighten permissions to owner-only.
    gk.KEY_FILE.write_text(secret + "\n", encoding="utf-8")
    os.chmod(gk.KEY_FILE, 0o600)
    key_id = "director-" + datetime.datetime.utcnow().strftime("%Y%m")
    print(f"Generated Director signing key at {gk.KEY_FILE} (mode 600).")
    print(f"Suggested key_id: {key_id}")
    print("This file is gitignored. Back it up securely; losing it means re-approving gates.")
    print("Alternatively export DOW_GATE_SECRET in your environment for headless/CI signing.")
    return 0


def cmd_approve(args):
    if args.decision not in VALID_DECISIONS:
        sys.stderr.write(f"Invalid --decision. Choose one of: {sorted(VALID_DECISIONS)}\n")
        return 1
    if args.decision == "Conditionally Approved" and not (args.conditions or "").strip():
        sys.stderr.write("Conditionally Approved requires non-empty --conditions.\n")
        return 1

    secret = gk.load_secret()
    if secret is None:
        sys.stderr.write(
            "No signing secret available. Run 'approve_gate.py init-key' or export "
            f"{gk.SECRET_ENV}. WITHOUT a secret, gates remain closed (fail-closed).\n")
        return 1

    state = gk.load_state()
    if args.gate not in state.get("gates", {}):
        sys.stderr.write(f"Unknown gate '{args.gate}'. Known: {list(state['gates'])}\n")
        return 1

    gate = state["gates"][args.gate]
    approval = {
        "decision": args.decision,
        "approver_role": args.approver_role,
        "approver_name": args.approver_name,
        "approved_utc": _now(),
        "conditions": (args.conditions or ""),
        "key_id": args.key_id,
    }
    payload = gk.canonical_payload(state.get("project"), args.gate, gate.get("phase"), approval)
    approval["payload_sha256"] = __import__("hashlib").sha256(payload.encode("utf-8")).hexdigest()
    approval["signature"] = gk.compute_signature(secret, payload)

    gate["approval"] = approval
    gate["status"] = args.decision
    gk.save_state(state)

    # Re-verify immediately so we never persist something the gatekeeper would reject.
    if not gk.approval_is_valid(state, args.gate, gate):
        sys.stderr.write("INTERNAL ERROR: written approval did not verify. Reverting.\n")
        return 1

    print(f"{args.gate} -> {args.decision} (signed by {args.approver_name}, "
          f"key_id={args.key_id}).")
    print(f"Signature: {approval['signature'][:16]}...")
    print("NOTE: also update the narrative sign-off in "
          ".governance/Phase_Gates/<gate>/gate-status.md to match.")
    return 0


def cmd_mark_ready(args):
    """Agent-invokable ceiling: READY FOR VERIFICATION only. Never an approval."""
    state = gk.load_state()
    if args.gate not in state.get("gates", {}):
        sys.stderr.write(f"Unknown gate '{args.gate}'.\n")
        return 1
    gate = state["gates"][args.gate]
    if gate.get("approval"):
        sys.stderr.write("Gate already has an approval record; refusing to downgrade.\n")
        return 1
    gate["status"] = "READY FOR VERIFICATION"
    gate["ready_for_verification_by"] = args.by
    gk.save_state(state)
    print(f"{args.gate} -> READY FOR VERIFICATION (by {args.by}). "
          f"This is NOT an approval; a signed Director approval is still required to open the gate.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="approve_gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-key")

    p = sub.add_parser("approve")
    p.add_argument("--gate", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--approver-role", required=True)
    p.add_argument("--approver-name", required=True)
    p.add_argument("--conditions", default="")
    p.add_argument("--key-id", default="director-" + datetime.datetime.utcnow().strftime("%Y%m"))

    pr = sub.add_parser("mark-ready")
    pr.add_argument("--gate", required=True)
    pr.add_argument("--by", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "init-key":
        return cmd_init_key()
    if args.cmd == "approve":
        return cmd_approve(args)
    if args.cmd == "mark-ready":
        return cmd_mark_ready(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
