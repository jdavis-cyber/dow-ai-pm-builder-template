# Documentation Map

> Template status: scaffold. A file's presence is not approval; approval requires a populated gate or decision record.

## Canonical Repo Surfaces

| Surface | Purpose | Expected Contents | Status Notes |
|---|---|---|---|
| `src/`, `services/`, `packages/` | Application source | UI, API, services, libraries | Gate-protected implementation surface |
| `database/`, `infrastructure/` | Data and deployment/runtime infrastructure | Schemas, migrations, IaC, containers | Gate-protected implementation surface |
| `.governance/` | Formal governance/compliance evidence | Phase gates, risk, standards, override records | Draft until approved by records/signatures |
| `docs/product/` | Product definition | PRD, user stories, classification | Discovery/review surface |
| `docs/architecture/` | Architecture records | ADRs, schemas, diagrams, threat model links | Discovery/review surface |
| `docs/decisions/` | Decision records | ADRs and governance decision records | Append-only where practical |
| `docs/governance-frameworks/` | Framework applicability | Framework status and applicability records | Gap-labeled until authoritative mappings exist |
| `docs/verification/` | Verification evidence | Command output, hashes, validation results | Append-only evidence surface |
| `docs/handoff/` | Continuation package | Restart prompts and navigation | Human/agent navigation surface |
| `orchestration/` | Agentic build logic | System spec, task board, sprint playbooks | Task status is not approval |
| `directives/` | Governing protocols | Integrity, governance, reporting directives | Template/process control surface |
| `.agent/`, `subagents/` | Agent identity/execution packages | SOUL files, TOMLs, runtime maps | Process/provenance surface |

## Non-Confusion Rule

Scaffolded, copied, or historical artifacts remain labeled as scaffolds until populated, verified, and approved.
