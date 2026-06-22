# Documentation Map

> Template status: scaffold. Replace bracketed fields during project instantiation. Do not treat this file as project approval evidence until populated and reviewed.

## Artifact Status

| Field | Value |
|---|---|
| Status | Draft |
| Approval State | Not Approved |
| Evidence Type | Template Scaffold |
| Owner | Program Analyst / Scrum Master |
| Last Updated | [YYYY-MM-DD] |

## Purpose

This map helps a future human, reviewer, assessor, or agent open one repository and find the current source, governance state, decisions, evidence, and handoff materials without needing a second governance repo.

## Canonical Repo Surfaces

| Surface | Purpose | Expected Contents | Status Notes |
|---|---|---|---|
| `src/` | Application source | UI, API, services, libraries | Gate-protected implementation surface |
| `services/` | Service/microservice source | Independently deployable services | Gate-protected implementation surface |
| `packages/` | Shared packages | Workspace libraries/modules | Gate-protected implementation surface |
| `database/` | Data layer | schemas, migrations, seed/reference data | Gate-protected implementation surface |
| `infrastructure/` | Deployment/runtime infrastructure | IaC, containers, deployment manifests | Gate-protected implementation surface |
| `execution/` | Optional/legacy implementation workspace | Stack-specific implementation if chosen | Gate-protected implementation surface |
| `.governance/` | Governance and compliance evidence | phase gates, risk, SoA, standards, reviews | Draft until approved by records/signatures |
| `docs/product/` | Product definition | PRD, user stories, RTVM | Discovery and review surface |
| `docs/architecture/` | Architecture records | ADRs, schemas, diagrams, threat model links | Discovery and review surface |
| `docs/decisions/` | Decision records | ADRs and governance decision records | Append-only when possible |
| `docs/verification/` | Evidence records | command output, hashes, validation results | Append-only evidence surface |
| `docs/handoff/` | Continuation package | restart prompts, documentation map, project guide | Human/agent navigation surface |
| `orchestration/` | Agentic build logic | system spec, tasks, sprint playbooks | Do not treat task status as approval |
| `directives/` | Governing protocols | integrity, governance, reporting directives | Template/process control surface |
| `.agent/`, `subagents/` | Agent identity/execution packages | SOUL files and TOML packages | Process/provenance surface |

## Required Project-Specific Links

Populate these during project instantiation or Gate 1 reconstruction.

| Question | Link / Path | Current State |
|---|---|---|
| What is the project? | `PROJECT.md` | [Draft / Complete] |
| What is the current phase/gate? | `.governance/Phase_Gates/` | [Not Approved / Ready / Approved] |
| What is the system spec? | `orchestration/system_spec.md` | [Draft / Complete] |
| What work is planned? | `orchestration/tasks.md` | [Draft / Active] |
| What product requirements govern the build? | `docs/product/` | [Draft / Approved] |
| What decisions shaped the build? | `docs/decisions/` and `docs/architecture/` | [Draft / Active] |
| What evidence supports current claims? | `docs/verification/` and `.governance/Cross_Cutting/Evidence_Index/` | [Draft / Active] |
| What must the next agent know? | `docs/handoff/project-continuation-guide.md` | [Draft / Current] |

## Non-Confusion Rule

A file's presence is not approval. Approval requires the relevant gate/decision record to show an approved status backed by PM/PO sign-off. Scaffolded, copied, or historical artifacts must remain labeled as such.
