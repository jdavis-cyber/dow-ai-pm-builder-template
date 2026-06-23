# DoW AI PM Builder Template

**A provider-agnostic template that instantiates a *governed* AI software factory — 15 accountable agents, phase-gated, with DoD-grade compliance scaffolding baked in.**

<p align="center">
  <img src="https://img.shields.io/badge/Governance-CPMAI%20%2F%20ISO%2042001%20%2F%20NIST%20AI%20RMF-6f42c1?style=for-the-badge" alt="Governance">
  <img src="https://img.shields.io/badge/DoD%20overlays-CMMC%20%2F%20FedRAMP%20%2F%20ATO-0A66C2?style=for-the-badge" alt="DoD overlays">
  <img src="https://img.shields.io/badge/Approach-Governance--as--Code-111?style=for-the-badge" alt="Governance as Code">
</p>

> ### For hiring managers — what this demonstrates
> This is a **governance-as-code blueprint for building AI software the way regulated and DoD environments require it.** Instead of bolting compliance on at the end, the template ships a 15-agent governed scrum team where a **Security & Compliance Officer sits in every phase gate**, projects start in *Draft / Not Approved* until evidence is populated, and framework mappings are explicitly fenced ("do not infer product compliance or fabricate mappings"). It's the operating model behind my thesis: **build the systems, govern the systems, defend the evidence** — turned into a reusable, validatable factory.
>
> **Bridges:** DoD/federal program execution · AI governance (CPMAI / ISO 42001 / NIST AI RMF) · security/compliance/audit · agentic GenAI orchestration · governance-as-code.
> **More:** [secondorderstrategy.com](https://secondorderstrategy.com) · author: Jerome Davis

## By the numbers

| Signal | Value |
| --- | --- |
| Governed team | **15 accountable agents** (mandatory roster) — Security & Compliance Officer in every gate |
| Specialization library | **136 capability packages** across **10 domains** under `subagents/global/voltagent/` |
| Ownership mapping | **272-entry** specialization → accountable-owner map |
| Governance directives | **11 directives** + **8 automation scripts** (validate, smoke-test, init, runtime-validate) |
| Default posture | Generated projects start **Draft / Not Approved** until phase-gate evidence exists |
| Framework coverage | CPMAI · ISO/IEC 42001 · NIST AI RMF · ISO/IEC 27001 (+ conditional CMMC / FedRAMP / HIPAA / SOC 2) |

## Operating model

The template creates a complete project package in a single repository: application source, governance records, decision logic, verification evidence, handoff materials, agent identities, runtime packages, and orchestration logic — all living together with clear folder boundaries. Work flows through phase gates; nothing advances to implementation until Sprint Zero discovery and gate evidence are populated.

```mermaid
flowchart TB
    Kick[KICKOFF phrase] --> SZ[Sprint Zero / Phase 0<br/>discovery interview]
    SZ --> Gate{Phase Gate}
    Gate -->|evidence required| SCO[[Security &amp; Compliance Officer<br/>in every gate]]

    subgraph Team [15 Accountable Agents · governed scrum team]
        direction LR
        Think[Thinkers ×4<br/>BA · UX · Arch]
        Build[Builders<br/>FE · BE · DB · DevOps]
        Verify[Verifiers<br/>QA · Test · Docs]
    end

    Gate --> Team
    Team --> Lib[136 VoltAgent specialization packages<br/>10 domains · 272 ownership entries]
    SCO --> Frame[Framework overlays<br/>CPMAI · ISO 42001 · NIST AI RMF · 27001<br/>+ conditional CMMC / FedRAMP / ATO]
    Team --> Out[Generated project<br/>Draft / Not Approved → evidence → approved]

    style SCO fill:#0A66C2,stroke:#06408a,color:#fff
    style Frame fill:#6f42c1,stroke:#4b2a86,color:#fff
    style Out fill:#1a7f37,stroke:#0b5023,color:#fff
```

## Factory team

- **15 accountable agents** are permanent and mandatory in the factory handoff model (rosters in `.agent/AGENT-ROSTER.md` and `.agent/souls/`).
- **Security & Compliance Officer is always installed** and participates in every phase gate.
- **136 specialization packages** under `subagents/global/voltagent/` (10 domain categories) are capability packages/tools mapped to accountable owners in `subagents/specialization-ownership-map.json`.

See `.agent/AGENT-ROSTER.md` and `subagents/SPECIALIZATION-LIBRARY.md`.

## Framework applicability

| Framework | Treatment |
|---|---|
| CPMAI | Baseline lifecycle backbone for the factory |
| ISO/IEC 42001 | Baseline AIMS management-system target for factory behavior |
| NIST AI RMF | Baseline risk-function overlay |
| ISO/IEC 27001 | Crosswalk candidate when source clauses are supplied/confirmed |
| ISO/IEC 27701 | Reference Needed — Not Authoritatively Mapped |
| CMMC / FedRAMP / HIPAA / SOC 2 | Conditional product overlays only |

**Do not infer product compliance or fabricate mappings.** This guardrail is intentional: the template scaffolds the *discipline and evidence trail*, not a compliance claim.

## Fresh clone validation

```bash
python3 automation/validate_template.py
python3 automation/smoke_test_template.py
```

## Instantiate a project

```bash
python3 automation/init_project.py my-project /tmp
cd /tmp/my-project
python3 automation/validate_runtime.py .codex/agents/runtime-manifest.json
```

For agent/operator kickoff, use the canonical phrase in `KICKOFF.md`:

```text
Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.
```

The factory should ask only for the minimum missing workspace detail, then let the Sprint Zero / Phase 0 interview collect mission, objectives, inputs, links, constraints, and authority boundaries.

Generated projects begin in **Draft / Not Approved** status. Sprint Zero discovery and phase gates must populate evidence before implementation proceeds.

## Runtime output

`.codex/agents/` is generated runtime output from `automation/install_subagents.py` and is ignored by git by default. The source of truth remains `subagents/` plus `.agent/souls/`.

## About the author

Built by **Jerome Davis** — a governance operator bridging DoD/federal program execution, security/compliance/audit, ISO 42001/27001 + NIST AI RMF, and hands-on agentic GenAI. This template is part of a portfolio demonstrating governance-as-code from agent runtime to auditor evidence.

🔗 **[secondorderstrategy.com](https://secondorderstrategy.com)** · companion projects: [Lliam-GOV](https://github.com/jdavis-cyber/lliam-gov) (governed AI agent) · [Priora](https://github.com/jdavis-cyber/priora) (AI lifecycle governance platform)
