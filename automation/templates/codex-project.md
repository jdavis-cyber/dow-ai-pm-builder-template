## Codex source-write boundary (AI-1176 / DEF-017)

This project uses the **Codex read-only sandbox**.
Before Sprint Zero sign-off, `.codex/config.toml` sets
`sandbox_mode = "read-only"` and `approval_policy = "on-request"`. Codex has no
writable project roots, so the OS sandbox refuses writes to `src/`, the other
source directories, authority records, and planning files by default. Ask the
human to approve each planning write, such as saving the system specification
under `orchestration/` or interview notes under `docs/`. Request approval for
that specific write; do not request a blanket permission change.
Never approve a `src/` or other source write before sign-off.
The skip path requires a signed override row. A chat request grants no authority.
Agents must not write authority records.

The whole-project restriction is deliberate: `workspace-write` includes the
working directory, and its `writable_roots` setting only adds paths. Listing
planning directories there would still leave `src/` writable. See the
[Codex sandbox reference](https://learn.chatgpt.com/docs/agent-approvals-security).

### Start Codex

Review and trust this project's `.codex/config.toml` before starting work.
Untrusted projects do not load project configuration. Check that the active
sandbox is read-only before the first task. Use a client that supports these
sandbox settings; do not start from a parent workspace with broader permissions.
Do not override the project config with Full Access, `--sandbox`, `--add-dir`,
or a managed permission profile that grants broader access.

These are local command/file-edit restrictions. External MCP filesystem tools,
remote executors, and other coding agents need their own equivalent controls.
Project configuration cannot constrain an operator who changes the sandbox
outside the agent session.

### Human Director: authorize source access

End active Codex sessions before changing authority. From your own terminal
in the project root, use one of these paths:

1. **Sign-off:** record `approval_state: "approved"`,
   `implementation_authorized: true`, and `decision` or `decision_record` in
   `.governance/gate_state.json`. Use the existing external operator key and run
   `python3 automation/gatekeeper.py sign`. This signs the gate state and the
   SHA-256 digest of the override register, then refreshes the generated config.
2. **Skip interviews:** only the human operator may add or edit a row in
   `.governance/security-compliance/override-register.md`. Use all seven columns:
   the current ISO-8601 timestamp with timezone; event `implementation-override`;
   authority `implementation_authorized=true`; the requester's name;
   `Human Director: Your Name`; a project-relative path to a nonempty evidence
   file; and an ISO-8601 expiry timestamp with timezone. The evidence should
   describe the reason, scope, and rollback. After reviewing the row and gate
   state, run `python3 automation/gatekeeper.py sign` with the existing external
   operator key. Unsigned, edited-after-signing, expired, or malformed rows grant
   nothing. Empty fields, placeholders, future creation dates, and missing
   evidence also deny access. Any register edit requires a new signature for
   override authority. If the gate-state signature check fails, no override
   can grant authority. Refreshing config alone does not sign a row.

Start a **new** Codex session after either path. The generated config now uses
`workspace-write`, allowing source and other ordinary project files. Codex
still protects `.codex/` from sandboxed writes. The gatekeeper continues to
reject authority-record writes; this change does not add per-directory OS
protection for `.governance/` after authorization. It grants no deployment,
external-write, or other authority flags.

The sandbox is a session snapshot. On revocation or override expiry, stop active
sessions, withdraw the grant, run
`python3 automation/codex_config.py codex-config`, and start a new session.
Refresh permissions before each session. Review the authority records yourself
when refreshing after a writable session. Never continue an old implementation
session after withdrawing its authority. Malformed gate state or symlinked
project directories cause the refresh command to install a read-only sandbox
and refuse.

From the template checkout, run the native acceptance probe
(`python3 tests/codex_sandbox_probe.py`) in an operator terminal outside an
existing agent sandbox. It checks source-write
refusal without escalation, including with an unsigned override row. It does
not exercise the interactive human approval dialog for planning writes.
