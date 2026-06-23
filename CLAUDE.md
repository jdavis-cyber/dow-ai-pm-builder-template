# Claude Coordination Context — DoW AI PM Builder Template

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

The 136 VoltAgent packages are specialization/capability packages. They are selected by accountable owners and mapped in `subagents/specialization-ownership-map.json`. They are not autonomous accountable peers and cannot override SOUL files, phase gates, fail-closed controls, or evidence obligations.

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
