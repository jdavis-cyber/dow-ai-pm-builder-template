# Security & Compliance Evidence Traceability Index

**Document Status:** Master index (updated per gate completion)
**Canonical Path:** `.governance/security-compliance/evidence-traceability.md`
**Authority:** `directives/ai-governance-framework.md`
**Last Updated:** 2026-03-30

---

## Purpose

This index links gate artifacts to security-compliance review outputs and approval records. It maintains traceability from gate decisions through regulated review and approval evidence.

**Important:** This is a **security-compliance-specific** index, NOT a replacement for the central evidence index at `.governance/Cross_Cutting/Evidence_Index/evidence-index.md`.

---

## Gate 1 — Business Understanding: Evidence Traceability

### Gate Overview

| Field | Value |
|-------|-------|
| Gate ID | Gate1_BusinessUnderstanding |
| Gate Path | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/` |
| Gate Status Record | `gate-status.md` |
| Gate Review Package | `phase-gate-review.md` |
| Approval Status | ⬜ Pending Initial Review |
| Compliance Profile | *To be populated from project classification* |

### Gate Artifacts Traceability

| Artifact | Location | Security Review Status | Approval Record | Compliance Notes |
|----------|----------|----------------------|-----------------|------------------|
| Gate Status Record | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/gate-status.md` | ⬜ Pending | — | Per-gate control record |
| Mission-Risk Profile | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/mission-risk-profile.md` | ⬜ Pending | — | Risk baseline establishment |
| Governance Scope Statement | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/governance-scope-statement.md` | ⬜ Pending | — | Control scope definition |
| Phase Gate Review Package | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/phase-gate-review.md` | ⬜ Pending | — | Formal gate package |

### Security Compliance Review Outputs

| Review Type | Location | Owner | Review Date | Findings Summary | Approval Status |
|------------|----------|-------|-------------|------------------|-----------------|
| Security Compliance Assessment | `.governance/security-compliance/reviews/gate1-security-compliance-review.md` | *TBD* | *Pending* | *To be populated* | ⬜ Pending |
| Control Mapping (if regulated) | `.governance/security-compliance/control-mappings/[framework]-gate1-control-mapping.md` | *TBD* | *Pending* | *To be populated* | ⬜ Pending |

### Approval Records

| Approval Type | Record Location | Authority | Decision | Approval Date | Signature Reference |
|--------------|-----------------|-----------|----------|---------------|-------------------|
| Program Analyst (Hard-Gate) | `.governance/security-compliance/approvals/gate1-approval-record-[YYYYMMDD].md` | Program Analyst | ⬜ Pending | — | — |
| Project Sponsor | `.governance/security-compliance/approvals/gate1-approval-record-[YYYYMMDD].md` | Project Sponsor | ⬜ Pending | — | — |
| Security & Compliance Officer (if regulated) | `.governance/security-compliance/approvals/gate1-approval-record-[YYYYMMDD].md` | Sec & Compliance Officer | ⬜ Pending/N/A | — | — |

### Residual Risk and Deviations

| Risk/Deviation ID | Description | Authority | Record Location | Status |
|------------------|-------------|-----------|---|--------|
| *None recorded yet* | — | — | — | — |

---

## Gate 2-6 Placeholders

*Traceability entries for Gates 2-6 will be added as they materialize. Phase-name remediation completed 2026-07-10: task boards use “CPMAI Phase N — <Name>” matching the GateN_<Name> directories and the activation matrix.*

| Gate | Path | Status | Phase-Name Issue |
|------|------|--------|-----------------|
| Gate2 | `.governance/Phase_Gates/Gate2_DataUnderstanding/` | ⬜ Not Started | Resolved 2026-07-10 (naming aligned) |
| Gate3 | `.governance/Phase_Gates/Gate3_DataPreparation/` | ⬜ Not Started | Resolved 2026-07-10 (naming aligned) |
| Gate4 | `.governance/Phase_Gates/Gate4_ModelDevelopment/` | ⬜ Not Started | Resolved 2026-07-10 (naming aligned) |
| Gate5 | `.governance/Phase_Gates/Gate5_ModelEvaluation/` | ⬜ Not Started | Resolved 2026-07-10 (naming aligned) |
| Gate6 | `.governance/Phase_Gates/Gate6_Operationalization/` | ⬜ Not Started | Resolved 2026-07-10 (naming aligned) |

---

## Cross-Cutting Governance References (Not Duplicated Here)

These authoritative baselines are referenced by gate artifacts but do NOT have separate security-compliance entries:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Risk Register | `.governance/Cross_Cutting/Risk_Register/risk-register.md` | Central project risk ledger (referenced by all gates) |
| Statement of Applicability | `.governance/Cross_Cutting/SoA/statement-of-applicability.md` | Control applicability baseline (cross-cutting) |
| Evidence Index | `.governance/Cross_Cutting/Evidence_Index/evidence-index.md` | Central artifact manifest (not gate-specific) |

**Rule:** When security-compliance artifacts reference regulatory requirements, they must link to the authoritative SoA rather than copying control requirements.

---

## File Naming Conventions

For future gates, use these conventions:

| Artifact Type | Pattern | Example |
|---|---|---|
| Security review | `gate<N>-security-compliance-review.md` | `gate1-security-compliance-review.md` |
| Approval record | `gate<N>-approval-record-<YYYYMMDD>.md` | `gate1-approval-record-20260330.md` |
| Control mapping | `<framework>-gate<N>-control-mapping.md` | `iso42001-gate1-control-mapping.md`, `dod-rmf-gate1-control-mapping.md` |
| Deviation | `deviation-<ID>-<description>.md` | `deviation-SEC36-R1-reconciliation.md` |

---

## Quality Rules

### Traceability Requirements

- [ ] Every gate artifact has a corresponding entry in this index
- [ ] Security review outputs are filed in `reviews/`
- [ ] Approval records are filed in `approvals/`
- [ ] Deviations and exceptions are filed in `deviations/`
- [ ] Control mappings are filed in `control-mappings/`
- [ ] All cross-references are markdown links (not bare paths)
- [ ] No duplication of content from `.governance/Cross_Cutting/`

### Update Protocol

| Event | Action | Owner |
|-------|--------|-------|
| Gate review complete | Add gate traceability row | Program Analyst |
| Approval decision made | Link approval record in `approvals/` | Gate Facilitator |
| Security review submitted | Link review output in `reviews/` | Security & Compliance Officer |
| Deviation approved | Create record in `deviations/` | Decision Authority |
| Phase-name remediation complete (Gates 2-6) | Update placeholder rows | Documentation SE |

---

## Integration with Overall Evidence Index

**This document is NOT a replacement for** `.governance/Cross_Cutting/Evidence_Index/evidence-index.md`.

**This document:** Links gate-specific security-compliance review outputs and approval evidence

**That document:** Central artifact inventory for all governance evidence (gates, cross-cutting, operational)

**Relationship:** Security-compliance traceability entries should reference the corresponding entry in the central Evidence Index.

---

## Revision History

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-03-30 | 1.0 | Documentation SE | Initial security-compliance traceability index |
