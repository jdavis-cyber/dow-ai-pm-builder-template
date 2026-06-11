# DoW AI PM Builder Template
### Discovery-First AI Software Factory — Regulated Edition

[![Governance: CPMAI v7](https://img.shields.io/badge/Governance-CPMAI%20v7-blue)](https://www.pmi.org/certifications/ai-project-management-cpmai)
[![Compliance: CMMC 2.0](https://img.shields.io/badge/Compliance-CMMC%202.0-red)](https://dodcio.defense.gov/CMMC/)
[![Compliance: FedRAMP](https://img.shields.io/badge/Compliance-FedRAMP-red)](https://www.fedramp.gov/)
[![Compliance: ISO 42001](https://img.shields.io/badge/AI%20Governance-ISO%2042001-orange)](https://www.iso.org/standard/81230.html)
[![Team: 15 Agents](https://img.shields.io/badge/Team-15%20Agents-green)](.agent/AGENT-ROSTER.md)
[![Specializations: 136](https://img.shields.io/badge/Specializations-136-purple)](subagents/global/)

---

> **Get started:** [INSTALL.md](INSTALL.md) — fresh machine to activated factory in under 15 minutes. **Demoing?** [DEMO.md](DEMO.md) — scripted auditor and executive walkthroughs.

## What This Is

A 15-agent autonomous software factory purpose-built for regulated, mission-critical development. Every agent in this system operates under a compliance envelope. Nothing ships without a Phase Gate. Nothing starts without a Definition of Ready. And nothing passes compliance review without the Security & Compliance Officer signing off — or generating a documented Override Register entry explaining exactly why she didn't.

This is not a template you configure. It is a governed system you activate.

---

## The 15-Agent Roster

### The Thinkers
| Agent | Role |
|:---|:---|
| Requirements BA | Extracts the "Why" — mission objectives, stakeholder constraints, DoD classification requirements |
| User Story BA | Translates requirements into INVEST-compliant acceptance criteria with regulatory traceability |
| UI/UX Designer | Human-centered design within ATO-scoped accessibility and Section 508 constraints |

### The Builders
| Agent | Role |
|:---|:---|
| Architecture SE | System design, ADRs, and DoD architecture compliance artifacts |
| Database Engineer | Schema governance, data classification, and audit trail design |
| Backend Developer | Secure-by-default API implementation under NIST SP 800-53 controls |
| Frontend Developer | Section 508 / WCAG 2.1 AA compliant UI execution |
| Pipeline DevOps | CI/CD pipelines, SBOM generation, and secure artifact management |
| Performance DevOps | Infrastructure tuning, load analysis, and SRE-level availability targets |

### The Critics
| Agent | Role |
|:---|:---|
| QA Engineer | Functional validation with regulatory traceability matrix coverage |
| Automation Test Engineer | Automated regression, chaos, and compliance smoke testing |
| Scrum Master | Sprint governance, Definition of Ready enforcement, Phase Gate coordination |
| Program Analyst | ISO 42001 artifact generation, CPMAI phase compliance, and reporting |

### The Compliance Layer
| Agent | Role |
|:---|:---|
| **Security & Compliance Officer** | Simultaneous enforcement of CMMC 2.0, FedRAMP, HIPAA, SOC 2, ISO 42001, and DoW CSRMC. Owns the Phase Gate. Operates Fail Closed. |

---

## Governance Model: Triple-Lock Protocol

This factory enforces predictable, auditable quality through three sequential gates before any code ships:

**Lock 0 — Spec Linter**
`automation/validate_spec.py` must pass with zero TBDs or TODOs before work begins. No ambiguity enters the build pipeline.

**Lock 1 — Definition of Ready**
The Scrum Master verifies that ADRs exist, dependencies are resolved, and the regulatory traceability matrix is populated. No guessing, ever.

**Lock 2 — Phase Gate (Security Officer)**
The Security & Compliance Officer reviews all six compliance frameworks simultaneously. If she cannot confirm compliance, the gate is blocked. Override requires a documented escalation in the Override Register — signed by the human Director.

### Fail Closed Protocol
The Security Officer defaults to **BLOCKED** when compliance cannot be confirmed. There is no "assume compliant." There is no "ship and fix later." Every override is permanent record.

---

## Execution Depth: Agent Specialization Library

Every agent in this factory is backed by a library of 136 specialized execution packages, wrapped in DoW-compliant TOML format and organized across 10 capability domains.

```
subagents/
├── global/                  # 20 DoW wrapper TOMLs for key specializations
│   ├── terraform-engineer.toml
│   ├── cloud-architect.toml
│   ├── sre-engineer.toml
│   ├── kubernetes-specialist.toml
│   └── ... (16 more)
│   └── voltagent/           # Full 136-TOML reference library
│       ├── 01-core-development/
│       ├── 02-language-specialists/
│       ├── 03-infrastructure/
│       ├── 04-quality-security/
│       ├── 05-data-ai/
│       ├── 06-developer-experience/
│       ├── 07-specialized-domains/
│       ├── 08-business-product/
│       ├── 09-meta-orchestration/
│       └── 10-research-analysis/
└── dod-regulated/           # 5 DoD-specific TOMLs
    ├── security-compliance-officer.toml
    ├── dod-compliance-auditor.toml
    ├── nist-rmf-analyst.toml
    ├── ato-documentation-specialist.toml
    └── iso42001-auditor.toml
```

Packages are activated through `install-config.json`. The baseline includes Scrum Master, Program Analyst, Documentation SE, Pipeline DevOps, and the Security & Compliance Officer. Project-specific and regulated overlays are added per engagement.

---

## SOUL Architecture: Two-Layer Agent Identity

Every agent operates on a two-layer model:

- **SOUL** (`.agent/souls/*.md`) — WHO the agent is. Identity, governing principles, interface contract, quality gate checklist. Immutable per deployment.
- **TOML** (`subagents/**/*.toml`) — HOW the agent executes. Working mode, focus areas, output contract. Composable per project.

TOML packages cannot weaken a SOUL's compliance requirements. They can only extend execution capability. This is enforced in `subagents/GOVERNANCE_WRAPPER.md`.

---

## Compliance Frameworks

This factory simultaneously enforces:

| Framework | Scope |
|:---|:---|
| CMMC 2.0 | Cybersecurity Maturity Model Certification — Level 2/3 |
| FedRAMP | Federal Risk and Authorization Management Program |
| HIPAA | Health Insurance Portability and Accountability Act (when applicable) |
| SOC 2 Type II | System and Organization Controls — Trust Service Criteria |
| ISO/IEC 42001 | AI Management System — Responsible AI governance |
| DoW CSRMC | Department of War Cyber Security Risk Management Charter |

---

## Activating the Factory

You don't configure this workspace. You wake it up.

1. Open this repository in Claude, Codex, or your AI IDE of choice.
2. Send one instruction:
   > "Initialize the project and begin Sprint Zero."
3. The Scrum Master coordinates the Sprint Zero interview sequence.
4. The factory does not build until the spec is locked, compliance is scoped, and the Security Officer has confirmed the regulatory framework for the engagement.

**Status**: Ready.
**Waiting on**: You.

---

*Built by Jerome Davis. Engineered for regulated environments where "ship fast and fix later" is not an option.*
