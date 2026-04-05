# AI Governance Framework Directive

**Source**: The Decisions That Come Before Scale: An AI Lifecycle Playbook for Regulated Environments
**Author**: Jerome Davis
**Directive Type**: Governance Reference — All Agents
**Primary Enforcer**: Program Analyst
**Last Updated**: 2026-04-05

---

## Purpose

This directive provides the synthesized operational reference for the AI Governance Framework as defined in *The Decisions That Come Before Scale: An AI Lifecycle Playbook for Regulated Environments*. It defines the governance structure, lifecycle methodology, compliance requirements, and artifact expectations that all agents must follow when executing AI projects within this workspace.

The full framework document is the authoritative source. This directive extracts the operational logic that agents need to produce compliant, traceable, and audit-ready work.

---

## Governing Standards

All projects governed by this framework must satisfy requirements from:

| Standard | Role in Framework |
|----------|-------------------|
| **CPMAI v7** | Lifecycle structure — 6 iterative phases with governance checkpoints |
| **ISO/IEC 42001** | AI Management System (AIMS) — Clauses 4–10 + Annex A controls (A.2–A.18) |
| **ISO/IEC 23894** | AI risk management principles — supplementary risk methodology |
| **NIST AI RMF 1.0** | Trustworthiness functions — Govern, Map, Measure, Manage |
| **NIST SP 800-53 Rev 5** | Security and privacy controls mapped per CPMAI phase |
| **DoW CSRMC** | Modernization overlay — MRP, CCV, AEP, Reciprocity, Resilience, Telemetry |
| **DoW RAISE Guidance** | Defense AI readiness and responsible AI principles for mission-aligned systems |
| **NIST SP 1270** | Bias identification and mitigation |
| **NIST AI 100-1** | Generative AI security considerations |
| **OMB M-25-21** | Federal AI governance and enterprise accountability expectations |
| **EU AI Act** | International regulatory expectations for high-risk AI systems |

These standards are not applied in isolation. The framework's crosswalk matrices harmonize them so that synthesized artifacts satisfy multiple standards simultaneously.

---

## CPMAI Lifecycle Phases

Every AI project follows the CPMAI six-phase lifecycle. Phase gates are hard gates — no advancement without Program Analyst sign-off.

### Phase I — Business Understanding
Define business objectives, mission alignment, stakeholders, governance scope, risk criteria, and success metrics. Produce the Mission Risk Profile, initial SoA, and Governance Scope Statement.

### Phase II — Data Understanding
Assess data sources, quality, provenance, lineage, bias risk, privacy constraints, and representativeness. Draft Telemetry Configuration and initiate the Reciprocity & Inheritance Register.

### Phase III — Data Preparation
Clean, transform, label, augment, and version datasets. Establish Automated Evidence Package for data lineage. Validate telemetry instrumentation in data pipelines.

### Phase IV — Model Development
Select modeling approaches, train, test, evaluate early-stage performance. Incorporate threat modeling, adversarial testing, and explainability. Produce initial CRPR and ACVR.

### Phase V — Model Evaluation
Independent evaluation of fairness, robustness, transparency, privacy, and mission alignment. Complete pre-deployment CCV cycle. Consolidate evidence into AEP. Produce Go/No-Go recommendation.

### Phase VI — Operationalization
Deploy to production, activate monitoring, telemetry, CCV cycles, and incident response. Validate resilience. Transition to continuous governance operations.

---

## Phase Gate Requirements

Each gate review uses a standardized template with eight sections:

1. **Project & Phase Information** — Metadata for traceability
2. **Purpose of the Gate** — What the gate validates
3. **Required Deliverables & Evidence Checklist** — Phase-specific mandatory artifacts
4. **Acceptance Criteria** — Minimum requirements for approval
5. **Findings & Required Corrective Actions** — Issues, gaps, and assignments
6. **Residual Risks / Deviations Accepted** — Documented exceptions
7. **Decision & Leadership Sign-Off** — Approval, conditional approval, or rejection
8. **Archival Instructions** — Repository location and evidence indexing

Gate decisions: **Approved** / **Conditionally Approved** (with corrective action timeline) / **Not Approved** (with required remediation).

---

## Decision Accountability and Executive Oversight

AI governance extends beyond the existence of controls, documentation, or technical safeguards. It requires demonstrable accountability for the decisions that introduce, authorize, and sustain AI-enabled capabilities within the enterprise. Because AI systems can influence outcomes in non-deterministic and evolving ways, governance must ensure that decision authority remains visible, revisitable, and actively exercised over time.

**Accountability is established by explicitly linking AI system artifacts to the decisions they support.** Business justification documents, risk assessments, Statements of Applicability, approval records, and operational review outputs are treated not merely as compliance evidence, but as decision records that capture the rationale, assumptions, and risk acceptance judgments made at each point in the lifecycle.

**Executive oversight is maintained through structured review mechanisms** that evaluate whether the conditions under which prior decisions were made continue to hold. As AI systems evolve through retraining, data changes, dependency updates, or expanded use, governance reviews reassess alignment with original intent, risk tolerance, and mission objectives. Accountability does not expire at deployment — it persists throughout operational use.

The governance model therefore requires that leadership roles remain engaged not only at initial approval gates, but during material change evaluations, periodic performance reviews, and continuous compliance validation cycles. These interactions provide traceable evidence that AI-related decisions are actively owned, monitored, and reaffirmed.

By framing governance artifacts as decision accountability instruments, the organization demonstrates that AI systems remain under explicit human authority, with clear ownership for outcomes, risk acceptance, and corrective action. This approach satisfies external accountability expectations from oversight bodies such as the U.S. Government Accountability Office, while remaining fully aligned with ISO/IEC 42001 management system principles.

---

## CSRMC Modernization Elements

All agents should be aware of these CSRMC elements that the Program Analyst enforces:

| Element | Purpose | Lifecycle Touchpoints |
|---------|---------|----------------------|
| Mission Risk Profile (MRP) | Mission-aligned risk evaluation | Phase I, updates II–VI |
| Critical Controls Identification | Prioritized security/resilience controls | Phase I–II |
| Telemetry Configuration | Real-time monitoring strategy | Phase II–III |
| Reciprocity & Inheritance Register | Reuse of validated controls | Phase II, updates III–VI |
| Cyber Resilience Posture Report (CRPR) | Resilience documentation | Phase IV–V, updates VI |
| Automated Evidence Package (AEP) | Audit-ready evidence bundle | Phase III–VI |
| Continuous Compliance Validation (CCV) | Automated compliance checks | Phase V–VI |
| Automated Control Validation Ruleset (ACVR) | Machine-readable CCV rules | Phase IV–V |

---

## AI Risk Taxonomy

All risks are classified using seven domains:

| Domain | Description | Examples |
|--------|-------------|----------|
| Technical | Model behavior, performance, reliability | Model drift, data drift, hallucinations, overfitting |
| Ethical | Fairness, transparency, responsible outcomes | Bias, unfair impact, lack of explainability |
| Operational | Business continuity, operational performance | System downtime, dependency failures |
| Cybersecurity | Adversarial threats, security vulnerabilities | Adversarial attacks, poisoning, model extraction |
| Privacy | Data protection, privacy violations | Leakage, reidentification, improper data handling |
| Regulatory | Compliance with laws, standards, policies | EU AI Act noncompliance, audit failures, contractual violations |
| Mission-Driven | Mission success, critical organizational functions | Mission degradation, performance shortfall |

---

## Evidence Categories

All evidence falls into six categories:

1. **Governance & Policy Evidence** — Policies, governance structure, ethical frameworks, leadership oversight
2. **Risk & Security Evidence** — Risk registers, threat assessments, resilience documentation, security controls, MRP
3. **Data Governance Evidence** — Data quality, lineage, privacy compliance, profiling results, pipeline integrity
4. **Model Development Evidence** — Experiments, performance metrics, explainability, bias assessments, robustness evaluations
5. **Operational & Monitoring Evidence** — Telemetry, CCV reports, incident response records, operational performance
6. **Gate Approvals & Decision Records** — Governance decisions, risk acceptance, deviations, executive approvals

---

## Governance Roles and Responsibilities

The following roles represent governance functions rather than job titles. They may be combined or distributed depending on the size, maturity, and structure of the organization.

| Role | Primary Responsibility | Escalation Authority |
|------|----------------------|---------------------|
| **Executive Sponsor** | Ultimate accountability for the AI system; approves risk acceptance and major governance actions | Final authority on risk acceptance |
| **AI Governance Lead** | Maintains framework alignment to ISO 42001, NIST AI RMF, and CSRMC; owns governance policies and lifecycle evidence | Escalation from Program Manager |
| **Program Manager** | Day-to-day project execution; phase gate readiness; cross-functional coordination | Routine decisions |
| **Data Lead / Data Steward** | Data quality, provenance, lineage, bias, and privacy across lifecycle | Flags data-driven risks |
| **ML/AI Engineer** | Model development, training, evaluation, explainability, and AEP contributions | Technical issues |
| **MLOps / Platform Engineer** | Deployment pipelines, telemetry, CCV activation, operational monitoring | Operational issues |
| **Security Officer / Cyber Analyst** | Cybersecurity, NIST SP 800-53 controls, adversarial threat modeling, CCV | Security findings |
| **Risk Officer** | AI Risk Register, residual risk monitoring, risk acceptance coordination, MRP | Risk threshold breaches |
| **Privacy Officer / Data Protection Lead** | Privacy regulations, data protection impact assessments, minimization and retention controls | Privacy incidents |
| **Ethics Officer** | Fairness, transparency, accountability, human oversight, bias mitigation, ISO 42001 Annex A alignment | Ethical risk findings |
| **Internal Audit** | Independent evaluation of framework conformance; certification readiness; evidence quality review | Audit findings |
| **Supplier/Vendor Manager** | AI-relevant external suppliers; control inheritance; supply chain risk; ongoing compliance monitoring | Supply chain risks |

### Escalation Model

1. **Routine project decisions** → Program Manager
2. **Governance decisions, deviations, exceptions, material changes** → AI Governance Lead
3. **Elevated or mission-impacting risk acceptance** → Executive Sponsor (Human Director)

---

## AI Governance Maturity Model

| Stage | Name | Description |
|-------|------|-------------|
| **1** | Foundational Awareness | Governance exists but lacks formal processes. AI experimentation with inconsistent oversight and documentation. |
| **2** | Structured Governance | Formalized roles, lifecycle processes, and risk management. Consistent evidence generation. Initial ISO 42001 and NIST AI RMF alignment. |
| **3** | Integrated Management System | AI governance fully integrated with QMS, ISMS, risk management, and cybersecurity. CSRMC-aligned monitoring begins. Consistent cross-program governance. |
| **4** | Continuous Assurance and Optimization | Continuous monitoring and CCV automation. Telemetry-driven governance. ISO 42001 certification ready. AI systems operate with continuous accountability and enterprise-level resilience. |

---

## Governance Cadence

| Level | Frequency | Focus | Participants |
|-------|-----------|-------|-------------|
| Operational Review | Weekly | Telemetry, drift, anomalies, issue escalation | Program Manager, Data Lead, ML Engineers |
| Governance Review | Bi-Weekly / Monthly | Risk register, SoA updates, documentation, CCV prep | AI Governance Lead, Security, Risk Officer |
| Executive Review | Quarterly | Risk acceptance, strategic alignment, performance | Executive Sponsor, Leadership |
| Audit & Compliance | Annual / Triggered | Internal audits, external assessments, certification prep | Governance Lead, Internal Audit, Compliance |

---

## Agent Compliance Obligations

Every agent on this team produces work that feeds into the governance evidence chain. Key obligations:

**Requirements BA / User Story BA**: Ensure requirements include governance, ethical, and compliance considerations. Requirements feed Phase I gate deliverables.

**Architecture SE**: Document architecture decisions in ADRs that reference security and resilience requirements. Architecture artifacts feed CRPR and threat model.

**Database Engineer**: Maintain data lineage, provenance, and quality documentation. Data artifacts feed Phase II/III gate deliverables and AEP.

**Backend Developer / Frontend Developer**: Follow secure development practices documented in the governance framework. Development artifacts feed Phase IV evidence.

**QA Engineer / Automation Test Engineer**: Test results must be traceable to acceptance criteria defined in governance. Testing artifacts feed Phase IV/V evidence and CCV rulesets.

**Pipeline DevOps / Performance DevOps**: Deployment and monitoring configurations must satisfy CSRMC telemetry and CCV requirements. Operational artifacts feed Phase VI gate.

**Documentation SE**: Ensure all governance documents follow ISO 42001 Clause 7.5 documentation control requirements. Support version control and archival.

**UI/UX Designer**: Ensure human oversight interfaces are designed per ISO 42001 Annex A human oversight requirements.

**Scrum Master**: Incorporate governance milestones (phase gates, governance reviews) into sprint planning. Coordinate with Program Analyst on compliance scheduling.

---

## Evidence Repository Structure

```
/Governance/
├── Phase_Gates/
│   ├── Gate1_BusinessUnderstanding/
│   ├── Gate2_DataUnderstanding/
│   ├── Gate3_DataPreparation/
│   ├── Gate4_ModelDevelopment/
│   ├── Gate5_ModelEvaluation/
│   └── Gate6_Operationalization/
├── Cross_Cutting/
│   ├── Risk_Register/
│   ├── SoA/
│   ├── CSRMC/
│   ├── Evidence_Index/
│   └── Governance_Cadence/
├── Phase_I/
├── Phase_II/
├── Phase_III/
├── Phase_IV/
├── Phase_V/
├── Phase_VI/
├── Management_Reviews/
├── Incident_Response/
└── Appendices/
```

---

*Version*: 2.0
*Last Updated*: 2026-04-05
*Source Document*: The Decisions That Come Before Scale: An AI Lifecycle Playbook for Regulated Environments by Jerome Davis
*Maintained By*: Program Analyst
*Applies To*: All agents in the workspace
*Change Summary (v1.1.1 → v2.0)*: Added ISO/IEC 23894 and EU AI Act to governing standards; updated OMB M-24-10 to OMB M-25-21; added DoW RAISE Guidance; added Decision Accountability section (§3.4); added Ethics Officer, Privacy Officer, Supplier/Vendor Manager, and Internal Audit roles; added 4-stage Maturity Model; updated DoD references to DoW; updated source document title.
