# ADR-002: Signed Implementation Overrides

## Status
Accepted by Human Director Rome, 2026-10-28 (AI-1176 / DEF-017, decision A2).

## Context

Gatekeeper and Codex config previously accepted unsigned override-register rows
as implementation authority, including when gate-state signature verification
failed. This contradicted the SR-08 rule that the override register grants no
authority on its own.

## Decision

- Only the human operator may add or edit rows in
  `.governance/security-compliance/override-register.md`. Agents may request an
  override but must not write authority records. Each implementation override
  names its requester and approving Human Director and cites a nonempty evidence
  file within the project describing the reason, scope, and rollback.
- The operator must review the gate state and register, then run
  `python3 automation/gatekeeper.py sign` with the existing external operator key.
  The command signs the gate state together with the register's SHA-256 digest.
  Both `check-action` and `codex-config` verify that signature and digest before
  accepting override authority. Config refresh alone does not sign the register.
- A row must use event `implementation-override` and authority
  `implementation_authorized=true`. Creation and expiry timestamps must include
  timezones; the current time must be at or after creation and before expiry.
  Empty fields, placeholders, missing evidence, and malformed rows grant nothing,
  even when the operator signs the register.
- Unsigned rows grant nothing. Any register edit invalidates override authority
  until the operator reviews and signs again. A failed gate-state signature check
  denies all override authority. The override grants implementation access only;
  it does not grant deployment, external-write, or authority-record write access.

## Consequences

The operator must sign existing override rows before using them. Gatekeeper
checks expiry on each action check; Codex config captures authority at refresh.
The operator must end active sessions on expiry or revocation, refresh with
`python3 automation/codex_config.py codex-config`, and start a new session.
The operator must also refresh before each session.

Under decision B1, the pre-authority config remains `read-only` and uses
`approval_policy = "on-request"` so the human can approve each planning write.
Never approve a `src/` or other source write before sign-off.
The skip path requires a signed override row and a new session after refresh.
