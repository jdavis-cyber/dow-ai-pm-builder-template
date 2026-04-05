# System Specification Document

**Project Name**: DoW PM Builder Template v4 Control-Plane Upgrade
**Status**: Draft for Section A with downstream sections locked pending specialist input
**Last Updated**: 2026-03-29

---

## Instructions for Agents

This document is the single source of truth for the project. Agents may act only on the sections owned by their specialty and only after upstream dependencies are validated. If a required detail is not present here, stop and escalate to the Scrum Master instead of guessing.

---

## A. System Overview

### Purpose & Problem Statement

The system is a discovery-first AI software factory template that initializes a governed multi-agent delivery workspace. Its purpose is to force project teams to capture requirements, architecture, governance, and verification inputs before implementation work begins, then materialize only the runtime agent bundles appropriate for the project profile.

The current problem is that the template has a packaging concept for `subagents/` and generated runtime agents, but it does not yet define the business-level system overview or the project-classification answers required to select those runtime bundles deterministically. Without this section, downstream roles will guess which agents, compliance overlays, and startup checks belong in a given initialized project, which breaks fail-closed behavior and weakens audit traceability.

### Target Users & Permissions

- `Human Director`: Defines mission, intended outcome, adoption risk, and mandatory compliance scope. Approves phase gates and final direction changes.
- `Scrum Master`: Controls sequencing and work start authority. May block execution when the spec, gates, or dependencies are incomplete.
- `Requirements BA`: Owns Section A and captures measurable outcomes, roles, and classification answers. May not invent architecture or implementation details.
- `Architecture SE and DevOps`: Consume the approved classification inputs to define packaging, runtime generation, startup validation, and environment behavior.
- `Program Analyst`: Converts approved discovery outputs into governance artifacts and sign-off evidence. May reject work that is not traceable to approved requirements.
- `Project Specialists`: Use only the runtime agents and constraints selected by the approved install profile. They may not self-activate excluded regulated overlays.

### Success Metrics & Constraints

- `Primary outcome`: A project can be initialized with one approved classification pass that selects the correct runtime agent set and governance overlays without manual per-agent copying.
- `Spec completeness target`: Section A names the system purpose, user roles, measurable success criteria, and classification inputs with no unresolved placeholders.
- `Gate 1 contribution target`: Downstream teams can implement `subagents/install-config.json`, startup validation, and documentation updates without inventing missing business or compliance assumptions.
- `Determinism requirement`: The same approved project classification answers must resolve to the same runtime agent set every time.
- `Fail-closed requirement`: Missing or contradictory classification inputs must stop installation and trigger escalation rather than allowing partial activation.
- `Isolation requirement`: Regulated overlays stay local to the initialized project and must not leak into unrelated projects or shared workspace assets.
- `Compliance scope`: The template must support CPMAI phase discipline for all projects and must support stronger overlays for ISO 42001, NIST AI RMF, NIST SP 800-53 Rev 5, DoD CSRMC, NIST SP 1270, NIST AI 100-1, and OMB M-24-10 when the project profile requires them.
- `Branch discipline`: Phase 0 control-plane work remains isolated from the dirty default branch until reviewed on the approved staging path.

### Project Classification Inputs For Install Profile

The install profile must be driven by explicit answers captured during Sprint Zero. These inputs are the minimum approved business and compliance classification fields for Phase 0.

1. `project_type`
   Allowed values: `standard`, `ai-ml`, `dod-regulated`, `hipaa`
   Meaning: Declares the dominant delivery and governance class of the project. This field determines whether regulated overlays are even eligible for activation.
2. `languages`
   Allowed values: explicit implementation languages such as `typescript`, `python`, `go`
   Meaning: Limits project-specific agent packages to the actual build stack.
3. `platforms`
   Allowed values: explicit target surfaces such as `web`, `api`, `cli`, `worker`, `infrastructure`
   Meaning: Prevents activation of delivery packages that do not match the product surface.
4. `requires_accessibility`
   Allowed values: `true`, `false`
   Meaning: States whether accessibility review and supporting specialists are mandatory at launch.
5. `requires_dod_controls`
   Allowed values: `true`, `false`
   Meaning: Separately captures whether DoD or federal control overlays are mandatory, even if the project also contains AI or general software work.
6. `requires_iso42001`
   Allowed values: `true`, `false`
   Meaning: Captures whether the project must operate inside the AI management system evidence model from day one.

### Classification Decision Rules

- If `project_type` is `dod-regulated`, then `requires_dod_controls` must be `true`.
- If `requires_dod_controls` is `true`, the Security and Compliance Officer support stack is mandatory.
- If `project_type` is `ai-ml`, then `requires_iso42001` must be explicitly answered and may not be inferred.
- If the project handles regulated federal or defense scope, the Human Director must declare that scope before implementation begins.
- If classification answers conflict, installation must stop and the Scrum Master must re-open discovery rather than choosing a best-effort profile.

### Source Questions For Sprint Zero

- What is the single primary outcome this initialized project must achieve?
- Which user and agent roles need authority in the project, and which roles must remain review-only?
- Is this project a standard software project, an AI or ML project, a DoD or federal regulated project, or a HIPAA-scoped project?
- Which implementation languages and delivery platforms are in scope at launch?
- Are accessibility, ISO 42001 controls, or DoD control overlays mandatory from day one?

---

## B. Architecture Specification

This section is intentionally unpopulated in this revision. Architecture SE and DevOps must supply the technology stack, runtime packaging design details, and infrastructure constraints after Section A is accepted.

---

## C. Interface Contracts

This section is intentionally unpopulated in this revision. Database, backend, frontend, and installer-facing contracts remain locked until the architecture and install-profile requirements are accepted.

---

## D. Agent Work Packages

### Requirements BA

- **Input Dependencies**: Director brief, template governance directives, packaging note, and Sprint Zero interview protocol
- **Output Contract**: Populate Section A and define the project-classification inputs that govern install-profile selection
- **Validation**: Section A is explicit, measurable, and free of placeholder text

### Architecture SE and DevOps

- **Input Dependencies**: Approved Section A classification inputs
- **Output Contract**: Define packaging logic, startup validation behavior, and runtime generation rules without changing the business classification contract
- **Validation**: Install behavior is deterministic and fail-closed

### Program Analyst

- **Input Dependencies**: Approved Section A and downstream implementation evidence
- **Output Contract**: Convert approved discovery outputs into governance artifacts and phase-gate evidence
- **Validation**: Governance artifacts trace back to approved requirements and classification decisions

---

## E. Decision Log

| Date | Agent | Decision Made | Rationale & Alternatives Considered |
|------|-------|---------------|-------------------------------------|
| 2026-03-29 | Requirements BA | Limited Phase 0 scope to Section A plus install-profile classification inputs | Parent board explicitly authorizes only missing spec context. Broader implementation or architecture authoring would violate separation of powers. |
| 2026-03-29 | Requirements BA | Kept the install-profile contract minimal and business-facing | Downstream roles need deterministic classification inputs, not an overbuilt schema. Expanding beyond the minimum would create implementation theater before approval. |
