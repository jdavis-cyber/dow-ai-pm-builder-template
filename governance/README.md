# Governance Enforcement Layer

This directory makes the repo's phase-gate governance **mechanically enforced** across all
three agent runtimes (Claude Code, Gemini CLI, Codex CLI), instead of relying on the LLM to
voluntarily obey prose. It closes five gaps: no executable control, rule decay over long
conversations, no separation of powers, Director-conversation-mistaken-for-approval, and
audit-shaped (forgeable) gate state.

## Three rings of defense (all share one brain)

1. **Runtime hooks** — `PreToolUse` hooks in each runtime call `automation/gatekeeper.py`, which
   **blocks writes/edits to `execution/`** while the active phase gate is closed, and re-injects
   gate state every turn via `SessionStart` / `UserPromptSubmit` (kills rule-decay).
   Configs: `.claude/settings.json`, `.gemini/settings.json`, `.codex/config.toml` (+ `.codex/hooks/hooks.json`).
   Shims: `governance/hooks/*.sh`.
2. **Automation gate** — `automation/run_factory.py` refuses to emit a build prompt for a builder
   role while the gate is closed (covers the autonomous loop / the Codex interactive-hooks bug #17532).
3. **Signed state** — `.governance/gate_state.json` is the canonical gate truth (durable: phase,
   gate statuses, approvals). A gate opens only via the Director-run, HMAC-signed
   `automation/approve_gate.py`. A gate that merely *says* "Approved" without a valid signature is
   treated as **closed** (fail-closed).

Volatile Lock 0 (spec-validation) state is kept separately in the gitignored
`.governance/gate_runtime.json`, refreshed on every session start — so refreshing it never dirties
the committed `gate_state.json`. Absent runtime file ⇒ Lock 0 is `UNKNOWN` (fail-closed).

## What is blocked when a gate is CLOSED

| Action | Verdict |
|---|---|
| Read anything (Read/Grep/Glob, `cat`, `ls`, read-only shell) | ✅ allowed |
| Write to `docs/`, `.governance/` narrative, `memory/`, `orchestration/tasks.md` | ✅ allowed |
| Write/Edit/patch to `execution/` (source code) | ⛔ blocked |
| Any write to `.governance/gate_state.json` | ⛔ blocked (always — only the signed CLI changes it) |
| Any `execution/` write while Lock 0 (spec validation) ≠ PASS | ⛔ blocked |

## Director workflow (one-time + per gate)

```bash
# 1. One-time: generate your signing key (gitignored). Until this exists, ALL gates are closed.
python3 automation/approve_gate.py init-key
#    (CI/headless alternative: export DOW_GATE_SECRET=<64-hex> instead of a key file)

# 2. When discovery for a phase is complete, approve its gate (this opens execution/ writes):
python3 automation/approve_gate.py approve \
    --gate Gate1_BusinessUnderstanding --decision Approved \
    --approver-role "Executive Sponsor" --approver-name "Your Name"

# 3. Check state / detect forgery at any time:
python3 automation/gatekeeper.py status
python3 automation/gatekeeper.py verify-consistency
```

An **agent's** ceiling is `python3 automation/approve_gate.py mark-ready --gate <G> --by <role>`
(status `READY FOR VERIFICATION`) — it can never approve.

## Why an agent cannot self-approve or be tricked by a chat request

- The hooks block any tool write to `.governance/gate_state.json`.
- Opening a gate requires a valid HMAC-SHA256 signature over the gate content; the secret lives
  only in your env var or a gitignored key file. The gatekeeper re-verifies the signature on every
  decision, so a hand-written "Approved" achieves nothing.
- A Director's conversational request ("let's add feature X") is not a signature and therefore is
  **not** an approval. Only running `approve_gate.py` is.

## Verify it works

```bash
bash governance/tests/test_enforcement.sh   # 17 checks; runs against a temp copy, no side effects
```

## Threat model note

This is defense-in-depth. The hard barrier against self-approval is the tool-write block plus the
signed state. The HMAC secret is the highest-value file in the repo — keep `.governance/.gate_key`
out of version control (it is gitignored). For cryptographic separation against a fully adversarial
in-environment process, host the signer off-machine and verify with a committed public key
(asymmetric signing) — a future hardening option beyond stdlib.
