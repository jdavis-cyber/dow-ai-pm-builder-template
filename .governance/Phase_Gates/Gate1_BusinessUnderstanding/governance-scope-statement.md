# Gate 1 Governance Scope Statement

**Document Status:** Template (awaiting project scope input)
**Canonical Path:** `.governance/Phase_Gates/Gate1_BusinessUnderstanding/governance-scope-statement.md`
**Authority:** `SEC-36`, `TEMPLATE-INDEX.md`, `directives/ai-governance-framework.md`
**Last Updated:** 2026-03-30

---

## Purpose

This document defines the governance boundary and control scope for the AI project. It establishes which AI systems, processes, and decisions fall within governance oversight and which fall outside.

---

## Project Identification

| Field | Value |
|-------|-------|
| Project Name | *To be populated* |
| Project Code | *To be populated* |
| Project Description | *To be populated* |
| Project Owner | *To be assigned* |
| Governance Sponsor | *To be assigned* |

---

## AI System Scope

### Systems In Scope

*List all AI systems, models, agents, or decision systems governed by this project.*

| System Name | Type | Purpose | Data Classification | Regulated Profile |
|-------------|------|---------|-------------------|-------------------|
| | *To be populated* | — | — | — |

### Systems Out of Scope

*List any AI-related systems excluded from Gate 1 governance with justification.*

| System Name | Reason for Exclusion | Compensating Controls |
|-------------|-------------------|----------------------|
| | *To be populated* | — |

---

## Governance Control Scope

### Controls In Scope

| Control Area | Included | Justification |
|--------------|----------|---------------|
| Data Governance | ⬜ Yes / No | *To be populated* |
| AI Model Development | ⬜ Yes / No | *To be populated* |
| Model Testing & Validation | ⬜ Yes / No | *To be populated* |
| Deployment & Operations | ⬜ Yes / No | *To be populated* |
| Monitoring & Maintenance | ⬜ Yes / No | *To be populated* |
| Security & Compliance | ⬜ Yes / No | *To be populated* |
| Performance & Fairness | ⬜ Yes / No | *To be populated* |
| Risk Management | ⬜ Yes / No | *To be populated* |
| Incident Response | ⬜ Yes / No | *To be populated* |

### Framework Applicability

| Framework | Applicable | Coverage | Notes |
|-----------|-----------|----------|-------|
| ISO 42001 (AI Management System) | ⬜ Yes / No | *Partial/Full* | *To be populated* |
| DoD RMF (if applicable) | ⬜ Yes / No | *Partial/Full* | *To be populated* |
| NIST AI RMF | ⬜ Yes / No | *Partial/Full* | *To be populated* |
| Project-Specific Standards | ⬜ Yes / No | *Partial/Full* | *To be populated* |

---

## Regulatory and Compliance Overlay

### Regulated Profile

| Dimension | Status | Details |
|-----------|--------|---------|
| DoD-Regulated Workload | ⬜ Yes / No | *To be populated if yes* |
| HIPAA-Regulated Data | ⬜ Yes / No | *To be populated if yes* |
| Other Regulatory Requirements | ⬜ Yes / No | *To be populated if yes* |

### Required Compliance Deliverables

| Deliverable | Responsible | Due Date | Completion Status |
|-------------|-------------|----------|------------------|
| | *To be assigned* | — | ⬜ Pending |

---

## Organizational Governance Structure

### Roles and Responsibilities

| Role | Name | Accountability | Escalation Path |
|------|------|-----------------|-----------------|
| Gate Owner | *To be assigned* | Gate execution and artifact completeness | Project Sponsor |
| Program Analyst | *To be assigned* | Control compliance verification | Gate Owner |
| Scrum Master / Delivery Lead | *To be assigned* | Sequencing and execution readiness | Program Manager |
| Security & Compliance Officer | *To be assigned (if regulated)* | Regulatory alignment and control mapping | Compliance Authority |
| Risk Officer | *To be assigned* | Risk identification and acceptance | CISO / CRO |

### Decision Authority Matrix

| Decision Type | Authority | Escalation |
|---------------|-----------|-----------|
| Entry Criteria Acceptance | Gate Owner + Program Analyst | Project Sponsor |
| Risk Acceptance | Decision Authority (TBD) | Executive Risk Board |
| Framework Deviation | *To be defined* | *To be defined* |
| Scope Change | Project Sponsor | PMO Director |

---

## Governance Artifacts and Deliverables

### Gate 1 Deliverables

| Artifact | Owner | Due Date | Status |
|----------|-------|----------|--------|
| `gate-status.md` | Program Analyst | — | ✅ Materialized |
| `phase-gate-review.md` | Gate Owner | — | ⬜ Pending |
| `mission-risk-profile.md` | Risk Officer | — | ⬜ Pending |
| `governance-scope-statement.md` | Governance Sponsor | — | ⬜ In Progress |

### Cross-Cutting Governance References

| Artifact | Path | Dependency |
|----------|------|-----------|
| Statement of Applicability | `.governance/Cross_Cutting/SoA/statement-of-applicability.md` | Control applicability baseline |
| Risk Register | `.governance/Cross_Cutting/Risk_Register/risk-register.md` | Project risk ledger |
| Evidence Index | `.governance/Cross_Cutting/Evidence_Index/evidence-index.md` | Artifact manifest |

---

## Governance Exceptions and Deviations

| Exception ID | Description | Authority | Approval Date | Expiration |
|--------------|-------------|-----------|---------------|-----------|
| | *No exceptions recorded* | — | — | — |

---

## Alignment Verification

- [ ] Scope statement aligns with `orchestration/system_spec.md` Section A
- [ ] Scope statement aligns with `docs/product/project-classification-inputs.md`
- [ ] Regulated profile is explicit (not inferred)
- [ ] All frameworks listed in `directives/ai-governance-framework.md` are addressed
- [ ] Roles and responsibilities match project org chart

---

## Approval and Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Governance Sponsor | *To be assigned* | — | ⬜ Pending |
| Gate Owner | *To be assigned* | — | ⬜ Pending |
| Project Sponsor | *To be assigned* | — | ⬜ Pending |

---

## Revision History

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-03-30 | 0.1 | Documentation SE | Initial template materialization per SEC-36 specification |
