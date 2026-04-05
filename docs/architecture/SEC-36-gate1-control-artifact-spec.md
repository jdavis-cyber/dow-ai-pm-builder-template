# SEC-36 Gate 1 Control Artifact And Evidence Path Spec

## Status

Approved governance specification for the Phase 0 control-plane lane. This document defines the minimum artifact contract needed so Gate 1 can run without improvisation against the current DoW PM Builder Template repository.

## Evidence Basis

This specification is derived only from approved or repo-grounded inputs:

- `orchestration/system_spec.md`
- `docs/product/project-classification-inputs.md`
- `docs/verification/sec-35-verify.md`
- `directives/ai-governance-framework.md`
- `directives/templates/TEMPLATE-INDEX.md`
- `directives/templates/phase-gate-review.md`
- `.governance/Phase_Gates/*`
- `.governance/Cross_Cutting/*`
- `subagents/dod-regulated/security-compliance-officer.toml`
- `directives/agent-activation-matrix.md`

## Decision Summary

1. `gate-status.md` is the canonical control artifact for every phase gate directory under `.governance/Phase_Gates/`.
2. Gate 1 evidence remains phase-owned under `.governance/Phase_Gates/Gate1_BusinessUnderstanding/`, while cross-cutting governance evidence continues to live under `.governance/Cross_Cutting/`.
3. A new `.governance/security-compliance/` tree is required for regulated review records, approval evidence, and control-traceability artifacts. It supplements, but does not replace, the existing `Cross_Cutting` structure.
4. `directives/templates/phase-gate-review.md` requires targeted Gate 1 corrections now and broader phase-name remediation before Gates 2-6 can be treated as compliant to the framework.

## Canonical Gate 1 Artifact Contract

### Gate 1 primary path

`/Volumes/WORKSPACE/DoW PM Builder Template/.governance/Phase_Gates/Gate1_BusinessUnderstanding/`

### Gate 1 required artifacts

| Artifact | Canonical Path | Purpose | Source Authority |
| --- | --- | --- | --- |
| Gate status control record | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/gate-status.md` | Single source of gate state, decision, findings, residual risk, and sign-off traceability | `SEC-36`, `directives/ai-governance-framework.md` |
| Phase gate review | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/phase-gate-review.md` | Formal gate package using the reusable template after correction | `directives/templates/phase-gate-review.md` |
| Mission Risk Profile | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/mission-risk-profile.md` | Gate 1 mission-aligned risk baseline | `directives/ai-governance-framework.md`, `TEMPLATE-INDEX.md` |
| Governance Scope Statement | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/governance-scope-statement.md` | Governance boundary and control-scope definition | `TEMPLATE-INDEX.md` |
| Statement of Applicability reference | `.governance/Cross_Cutting/SoA/statement-of-applicability.md` | Cross-cutting control applicability baseline referenced by Gate 1 | `directives/ai-governance-framework.md` |
| Risk Register reference | `.governance/Cross_Cutting/Risk_Register/risk-register.md` | Cross-cutting risk ledger referenced by Gate 1 | `directives/ai-governance-framework.md` |
| Evidence index reference | `.governance/Cross_Cutting/Evidence_Index/evidence-index.md` | Central evidence manifest referenced by gate artifacts | `directives/ai-governance-framework.md` |

### Gate 1 minimum `gate-status.md` contract

Every gate directory must contain a `gate-status.md` file with the following sections and fields.

#### 1. Metadata

- `Gate ID`: `Gate1_BusinessUnderstanding`
- `Lifecycle Phase`: `Phase I - Business Understanding`
- `Project Name`
- `Project Code`
- `Gate Status`: `not_started | in_progress | review_ready | approved | conditionally_approved | not_approved`
- `Review Date`
- `Last Updated`
- `Gate Owner`
- `Gate Facilitator`
- `Decision Authority`
- `Regulated Profile`: record `project_type`, `requires_dod_controls`, and `requires_iso42001`
- `Source Baseline`: paths for `orchestration/system_spec.md` and `docs/product/project-classification-inputs.md`

#### 2. Entry Criteria

Checklist confirming:

- `orchestration/system_spec.md` Section A is approved and populated.
- `docs/product/project-classification-inputs.md` is present and internally consistent.
- Required Gate 1 artifact paths exist or are explicitly marked missing.
- Regulated overlay decision is explicit, not inferred.

#### 3. Evidence Ledger

One row per required artifact with:

- `Artifact`
- `Required`
- `Status`
- `Canonical Path`
- `Reviewer`
- `Notes`

The ledger must include the Gate 1 artifact set above plus references to cross-cutting SoA, Risk Register, and Evidence Index.

#### 4. Findings And Corrective Actions

Table fields:

- `Finding ID`
- `Description`
- `Severity`
- `Owner`
- `Due Date`
- `Verification Method`
- `Status`

#### 5. Residual Risk And Accepted Deviations

Table fields:

- `Risk or Deviation ID`
- `Description`
- `Authority`
- `Conditions`
- `Expiration or Review Trigger`

#### 6. Gate Decision

- `Decision`: `approved | conditionally_approved | not_approved`
- `Decision Rationale`
- `Next Phase Authorization`
- `Blocked Dependencies`

#### 7. Required Sign-Offs

Required sign-off rows:

- `Program Analyst` — required for every gate because the framework defines Program Analyst sign-off as the hard-gate approval control.
- `Human Director or Project Sponsor` — required for business approval and mission authority.
- `Scrum Master` — required to acknowledge sequencing and execution-unblock state.
- `Security & Compliance Officer` — required when `project_type` is `dod-regulated` or `hipaa`, or when `requires_dod_controls` or `requires_iso42001` is `true`.

Each sign-off row must capture:

- `Name`
- `Role`
- `Decision`
- `Date Reviewed`
- `Date Approved`
- `Signature or approval record reference`
- `Comments`

#### 8. Archival Record

- `Primary Archive Path`
- `Evidence Index Entry`
- `Security-Compliance Traceability Entry`
- `Retention Notes`

## Canonical `.governance/security-compliance/` Structure

### Purpose

This tree stores regulated review outputs and approval evidence that belong to the security-compliance lane. It must not duplicate the authoritative Risk Register, SoA, or generic Evidence Index already defined under `.governance/Cross_Cutting/`.

### Required structure

```text
.governance/security-compliance/
├── README.md
├── evidence-traceability.md
├── reviews/
├── approvals/
├── deviations/
└── control-mappings/
```

### Directory rules

| Path | Required Contents | Notes |
| --- | --- | --- |
| `.governance/security-compliance/README.md` | Purpose, ownership, and path rules | Must state that cross-cutting artifacts stay authoritative in `Cross_Cutting` |
| `.governance/security-compliance/evidence-traceability.md` | Index linking gate artifacts to review outputs and approval records | Security-compliance-specific index, not a replacement for the main evidence index |
| `.governance/security-compliance/reviews/` | Gate-specific reviewer notes, checklists, and compliance review memos | Example file naming: `gate1-security-compliance-review.md` |
| `.governance/security-compliance/approvals/` | Signed approval records, formal concurrence notes, and risk-acceptance records | Link from `gate-status.md` sign-off rows |
| `.governance/security-compliance/deviations/` | Approved deviations and exception records | Must cross-reference residual risk entries |
| `.governance/security-compliance/control-mappings/` | Control crosswalks and requirement mappings used to justify regulated review decisions | Use references to SoA/CSRMC rather than copying them |

### Path ownership

- Gate-owned evidence stays in `.governance/Phase_Gates/<Gate>/`.
- Cross-cutting governance baselines stay in `.governance/Cross_Cutting/`.
- Security review outputs and approval evidence stay in `.governance/security-compliance/`.

## Exact Corrections Required In `directives/templates/phase-gate-review.md`

### Immediate corrections required for Gate 1

1. Add `Gate ID`, `Canonical Repository Path`, and `Source Baseline` fields to the metadata section.
2. Add `gate-status.md` as a required control artifact for every gate, with Gate 1 path `.governance/Phase_Gates/Gate1_BusinessUnderstanding/gate-status.md`.
3. Replace generic evidence placeholders in `Evidence Organization` with explicit repository references:
   - Primary repository: `.governance/Phase_Gates/Gate1_BusinessUnderstanding/`
   - Index/Manifest: `.governance/Cross_Cutting/Evidence_Index/evidence-index.md`
   - Security/compliance traceability: `.governance/security-compliance/evidence-traceability.md`
4. Add a required sign-off row for `Program Analyst`.
5. Add conditional sign-off logic for `Security & Compliance Officer` when the regulated profile requires it.
6. Update archival instructions so approval documents reference `.governance/security-compliance/approvals/` and supporting evidence references the gate-specific path, not generic storage text.
7. Replace Gate 1 deliverable location placeholders with the canonical Gate 1 and cross-cutting paths defined in this specification.

### Broader template defects that must be corrected before Gates 2-6 are used

The current reusable template claims CPMAI alignment but uses phase names that do not match `directives/ai-governance-framework.md`.

| Current Template Phase | Required Framework Phase |
| --- | --- |
| `Phase 2 - Data Management & Preparation` | `Phase II - Data Understanding` |
| `Phase 3 - Model Development & Training` | `Phase III - Data Preparation` |
| `Phase 4 - Evaluation & Validation` | `Phase IV - Model Development` |
| `Phase 5 - Deployment & Operations` | `Phase V - Model Evaluation` |
| `Phase 6 - Monitoring & Maintenance` | `Phase VI - Operationalization` |

This defect does not block the Gate 1 artifact package, but it is a compliance defect for every later gate and must be remediated before the reusable template can be treated as framework-accurate.

## Residual Risks

| ID | Risk | Impact | Required Follow-up |
| --- | --- | --- | --- |
| SEC36-R1 | `SEC-37` implementation scaffolding was produced before this spec landed | Provisional file paths or assumptions may differ from the approved control-artifact contract | DevOps must reconcile generated scaffolding against this spec before review closure |
| SEC36-R2 | Main evidence index file is referenced by the framework but not yet materialized in the repo | Gate packages can become inconsistent or hard to audit | Implement the evidence index before first formal gate review |
| SEC36-R3 | Standing operator docs still contain stale Drive folder names or IDs | Review artifacts can be misrouted | Keep Outbox delivery on the verified folder id and correct standing instructions separately |

## Recommended Downstream Sequence

1. Create `gate-status.md` in each `.governance/Phase_Gates/<Gate>/` directory using the contract above.
2. Create the `.governance/security-compliance/` tree and its traceability index.
3. Patch `directives/templates/phase-gate-review.md` with the immediate Gate 1 corrections.
4. Reconcile `SEC-37` provisional scaffolding against the approved artifact and evidence paths.
5. Schedule the broader phase-name remediation for Gates 2-6 before any later gate package is authored.
