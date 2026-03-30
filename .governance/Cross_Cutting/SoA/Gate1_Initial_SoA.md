# Statement of Applicability (SoA) — Gate 1 Initial Assessment

**Project**: AI Governance Framework — Phase 0 Control-Plane Pilot  
**Prepared By**: Pipeline DevOps  
**Date**: 2026-03-30  
**Framework**: Enterprise AI Governance & Lifecycle Management Framework v1.1.1  
**Standard**: ISO/IEC 42001:2023 (AI Management System)  
**Clause**: 6.2 — Determining the scope of the AIMS

---

## Purpose

The Statement of Applicability (SoA) documents which ISO 42001 controls are applicable to this project and which are deferred to later phases. Phase I focuses on governance surfaces; Phase III–VI will expand to operational and technical controls.

**Scope**: Phase 0 Control-Plane Pilot (Governance Infrastructure)

---

## ISO 42001 Control Applicability (Phase I Assessment)

### Clause 4: Context of the Organization

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **4.1** | Understanding the organization and its context | **Applicable** | Mission statement and stakeholder context defined | ✓ Complete |
| **4.2** | Understanding needs and expectations of interested parties | **Applicable** | Stakeholder matrix and roles identified | ✓ Complete |
| **4.3** | Determining scope of AIMS | **Applicable** | Governance scope statement prepared | ✓ Complete |
| **4.4** | AIMS | **Deferred to Phase III** | Operational AIMS deferred to Phase III (Data Preparation) | Planned |

---

### Clause 5: Leadership and Commitment

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **5.1** | Leadership and commitment | **Applicable** | Executive sponsor and PA roles defined | ✓ Complete |
| **5.2** | Policy | **Applicable** | Governance policy (framework directive) documented | ✓ Complete |
| **5.3** | Organizational roles, responsibilities, and authorities | **Applicable** | Stakeholder matrix and escalation model defined | ✓ Complete |

---

### Clause 6: Planning

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **6.1** | Actions to address risks and opportunities | **Applicable** | Risk taxonomy and mission risk profile created | ✓ Complete |
| **6.2** | Determining scope of AIMS | **Applicable** | Governance scope statement (this phase) | ✓ Complete |
| **6.3** | Determining AI management objectives and planning to achieve them | **Applicable** | Phase gates and success metrics defined | ✓ Complete |
| **6.4** | Planning of changes | **Deferred to Phase III** | Change management procedures deferred to operational phase | Planned |

---

### Clause 7: Support

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **7.1** | Resources | **Applicable** | Team composition and roles assigned | ✓ Complete |
| **7.2** | Competence | **Deferred to Phase II** | Competency assessment deferred to Data Understanding | Planned |
| **7.3** | Awareness | **Applicable** | Framework directive provides operational reference | ✓ Complete |
| **7.4** | Communication | **Applicable** | Governance cadence and review cycles defined | ✓ Complete |
| **7.5** | Documented information | **Applicable** | Gate documentation standards and evidence repository established | ✓ Complete |

---

### Clause 8: Operation

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **8.1** | Operational planning and control | **Deferred to Phase II** | Operational control procedures deferred to data handling phase | Planned |
| **8.2** | Risk and opportunities related to AI | **Deferred to Phase IV** | AI technical risks deferred to model development | Planned |
| **8.3** | Design and development of AI systems | **Deferred to Phase IV** | Model design/development governance deferred to Phase IV | Planned |
| **8.4** | Procurement | **Deferred to Phase III** | Data source procurement deferred to Phase III | Planned |
| **8.5** | Production and service provision | **Deferred to Phase VI** | Operationalization deferred to Phase VI | Planned |
| **8.6** | Release of AI systems | **Deferred to Phase VI** | Production release governance deferred to Phase VI | Planned |
| **8.7** | Control of externally provided processes, products, or services | **Deferred to Phase III** | Third-party data control deferred to Phase III | Planned |

---

### Clause 9: Performance Evaluation

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **9.1** | Monitoring, measurement, analysis, and evaluation | **Deferred to Phase V** | CCV and performance evaluation deferred to Phase V | Planned |
| **9.2** | Internal audit | **Deferred to Phase VI** | Internal audit procedures deferred to Phase VI | Planned |
| **9.3** | Management review | **Applicable** | Governance review cadence (operational, bi-weekly, quarterly, annual) defined | ✓ Complete |

---

### Clause 10: Improvement

| Control | Title | Phase I Applicability | Rationale | Status |
|---------|-------|----------------------|-----------|--------|
| **10.1** | General | **Deferred to Phase V** | Continuous improvement procedures deferred to Phase V (Model Evaluation) | Planned |
| **10.2** | Nonconformity and corrective action | **Deferred to Phase III** | Nonconformity procedures deferred to data handling phase | Planned |
| **10.3** | Continual improvement | **Deferred to Phase VI** | Continuous improvement governance deferred to Phase VI | Planned |

---

## Annex A: AI-Specific Controls (Phase I Assessment)

ISO 42001 Annex A provides 18 additional AI-specific controls. Phase I applicability:

| Control | Title | Phase I | Rationale |
|---------|-------|---------|-----------|
| **A.2** | Governance of AI | **Applicable** | Governance structure and decision authority defined | ✓ |
| **A.3** | Identification of AI systems in scope | **Deferred to Phase II** | AI system boundaries deferred to Data Understanding phase | Planned |
| **A.4** | Risk management for AI systems | **Deferred to Phase IV** | AI-specific risk management deferred to model development | Planned |
| **A.5–A.18** | Data governance, transparency, human oversight, bias mitigation, etc. | **Deferred to Phases II–VI** | AI-specific controls deferred to operational phases | Planned |

---

## Phase I SoA Summary

### Applicable Controls (Phase I)

**Clause 4** (Context): 4.1, 4.2, 4.3 ✓  
**Clause 5** (Leadership): 5.1, 5.2, 5.3 ✓  
**Clause 6** (Planning): 6.1, 6.2, 6.3 ✓  
**Clause 7** (Support): 7.1, 7.3, 7.4, 7.5 ✓  
**Clause 9** (Evaluation): 9.3 ✓  
**Annex A** (AI-Specific): A.2 ✓  

**Total Phase I Controls**: 11/28 core controls + 1/18 Annex A controls

### Deferred Controls (Phases II–VI)

- **Phase II** (Data Understanding): Clauses 7.2, 8.1, 8.4, 8.7, A.3
- **Phase III** (Data Preparation): Clauses 4.4, 6.4, 8.1, 8.4, 8.7, 10.2, A.5–A.18
- **Phase IV** (Model Development): Clauses 8.2, 8.3, A.4, A.5–A.18
- **Phase V** (Model Evaluation): Clauses 9.1, 10.1, A.4–A.18
- **Phase VI** (Operationalization): Clauses 8.5, 8.6, 9.2, 10.3, A.15–A.18

---

## Justification for Phase I Scope

### Why Phase I Controls Are Sufficient

1. **Governance First**: Control-plane governance must be established before operational controls can be implemented.
2. **Evidence Foundation**: Phase I builds evidence repository and documentation standards (Clause 7.5) that downstream controls depend on.
3. **Decision Authority**: Escalation and approval workflows (Clauses 5.1–5.3) are prerequisites for all downstream gate reviews.
4. **Risk Taxonomy**: AI Risk Taxonomy (Clause 6.1) provides framework for Phase II–VI risk assessments.

### Why Deferred Controls Are Inappropriate for Phase I

1. **No Data Yet**: Clauses 8.4, 8.7 (data procurement/control) require Phase II data source inventory.
2. **No Models Yet**: Clauses 8.2, 8.3 (AI design/development) require Phase IV model development.
3. **No Operations Yet**: Clauses 8.5, 8.6 (release/production) require Phase VI operationalization.
4. **No Measurement Yet**: Clauses 9.1, 9.2 (monitoring, audit) require operational metrics (Phase V–VI).

---

## SoA Update Timeline

This SoA will be updated at each phase gate:

| Phase | Gate | SoA Update Focus |
|-------|------|-----------------|
| **Phase II** | Gate 2 | Add data governance controls (A.5, 8.4, 8.7) |
| **Phase III** | Gate 3 | Add data preparation and evidence controls (10.2, A.7) |
| **Phase IV** | Gate 4 | Add AI-specific risk and development controls (A.4, 8.2, 8.3) |
| **Phase V** | Gate 5 | Add performance evaluation and CCV controls (9.1, 10.1) |
| **Phase VI** | Gate 6 | Add operationalization and continuous improvement controls (8.5, 8.6, 10.3) |

---

## Approval & Custody

**Prepared By**: Pipeline DevOps (a1567652-3092-4800-9004-fb67c6ca0805)  
**Reviewed By**: [Pending CTO/AI Governance Lead]  
**Approved By**: [Program Analyst — pending SEC-39]  
**Custodian**: AI Governance Lead  
**Next Review**: Phase II gate (Data Understanding)

---

*SoA Version*: 1.0  
*Reference Standard*: ISO/IEC 42001:2023 (AI Management System)  
*Framework Source*: Enterprise AI Governance & Lifecycle Management Framework v1.1.1  
*Related Issues*: [SEC-34](/SEC/issues/SEC-34), [SEC-36](/SEC/issues/SEC-36), [SEC-67](/SEC/issues/SEC-67)
