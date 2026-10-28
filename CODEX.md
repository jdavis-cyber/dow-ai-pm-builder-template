# Codex Coordination Context — DoW AI PM Builder Template

## Startup Protocol

Every agent must read, in order:

1. `PROJECT.md` — current project/package mission and scope.
2. `orchestration/system_spec.md` or `orchestration/system-spec-template.md` — the relevant system specification section.
3. `.codex/agents/runtime-manifest.json` when present — confirm the runtime package is installed before acting.
4. This provider coordination file — Claude, Codex, and Gemini carry the same operating model.
5. `factory.config.example.json` and `automation/governed_factory.py` when autonomous execution is expected — the factory is provider-neutral; runtime adapters execute tasks, but governance remains repo-owned.
6. `directives/structural-integrity-protocol.md` — phase-gate and traffic-cop requirements.
7. `directives/ai-governance-framework.md` and `directives/factory-governance-scope.md` — factory-governance evidence obligations.
8. `orchestration/tasks.md` — current task board and gate posture.

If the previous phase gate is not approved, agents stop and switch to discovery, documentation, remediation, or escalation. Do not perform implementation work without documented readiness.

## Operating Model

This repository is a provider-agnostic, single-repository AI software factory template. It instantiates one authoritative project package containing application source, governance records, task orchestration, decision records, validation evidence, handoff materials, and agent identity/runtime packages.

The permanent team is a **15-agent governed scrum team**:

- Requirements BA (`requirements-ba`)
- User Story BA (`user-story-ba`)
- UI/UX Designer (`ui-ux-designer`)
- Architecture SE (`architecture-se`)
- Database Engineer (`database-engineer`)
- Backend Developer (`backend-developer`)
- Frontend Developer (`frontend-developer`)
- Pipeline DevOps (`pipeline-devops`)
- Performance DevOps (`performance-devops`)
- QA Engineer (`qa-engineer`)
- Automation Test Engineer (`automation-test-engineer`)
- Scrum Master (`scrum-master`)
- Program Analyst (`program-analyst`)
- Documentation SE (`documentation-se`)
- Security & Compliance Officer (`security-compliance-officer`)

Security & Compliance Officer is always installed and participates in every phase gate. It enforces fail-closed findings, compliance gate evidence, and override-register requirements. Program Analyst authors and maintains governance evidence and management-system artifacts; it does not waive Security & Compliance Officer gates.

## Specializations

The 156 specialization packages (136 vendored VoltAgent packages plus 20 governed execution-depth wrappers at subagents/global/) are capability packages. They are selected by accountable owners and mapped in `subagents/specialization-ownership-map.json`. They are not autonomous accountable peers and cannot override SOUL files, phase gates, fail-closed controls, or evidence obligations.

## Evidence Standard

Every consequential workflow leaves objective evidence: task assignment, upstream inputs, outputs, verification command or method, handoff record, self-annealing record when defects occur, phase-gate decision, and evidence-index update. Local files are scaffolds until populated and verified.

## Required Validation Commands

- `python3 automation/validate_runtime.py .codex/agents/runtime-manifest.json`
- `python3 automation/validate_spec.py --mode template orchestration/system-spec-template.md`
- `python3 automation/validate_tasks.py orchestration/task-board-template.md`
- `python3 automation/validate_template.py`
- `python3 automation/smoke_test_template.py`

## Phase Gate Protocol

The Scrum Master coordinates phase movement. Security & Compliance Officer must review gate evidence. Program Analyst maintains governance artifacts. A gate is approved only when the gate record explicitly says approved and cites evidence; scaffold presence is not approval.

## Codex source-write boundary (AI-1176 / DEF-017)

Before Sprint Zero sign-off, Codex uses `sandbox_mode = "read-only"` and
`approval_policy = "on-request"` in `.codex/config.toml`. The sandbox blocks
project writes by default. Ask the human to approve each planning write to
planning files such as `orchestration/system_spec.md` or `docs/interview-notes.md`.
Never approve a `src/` or other source write before sign-off.
The skip path requires a signed override row; a chat request grants no authority.
Agents must not write authority records.

Only the human operator may add or edit an implementation override row, with
named Human Director approval, evidence, and a timezone-aware expiry. The operator
must run `python3 automation/gatekeeper.py sign` with the existing external key
so the signature covers both the gate state and the override register digest.
Unsigned, edited-after-signing, expired, or malformed rows grant nothing.
A failed gate-state signature check also denies override authority.

Follow the configuration, trust, refresh, and session-restart instructions in
[Codex project guidance](automation/templates/codex-project.md). Run
`python3 automation/codex_config.py codex-config` from the project root to
refresh permissions, then start a new session. Refresh before each session
and stop active sessions when authority expires or is withdrawn.
