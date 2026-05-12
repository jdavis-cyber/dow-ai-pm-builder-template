# Claude Code - Multi-Agent Orchestration Context

## 1. MANDATORY: Session Startup Protocol (Double-Lock Check)

Every agent MUST follow this sequence. Skipping steps or the order of files below is a Process Violation.

1. **PROJECT.md**: Read the current mission and scope.
2. **orchestration/system_spec.md**: Read the specific section of the Spec that your SOUL file depends on. Do not hallucinate assumptions or execute without this context.
3. **.codex/agents/runtime-manifest.json** (when present): Confirm your runtime package is installed before acting. Missing required TOMLs are an install failure, not an agent improvisation opportunity.
4. **CLAUDE.md**: [THIS FILE] Verify the team structure and your specific mandate.
5. **structural-integrity-protocol.md**: Read the Phase Gate and "Traffic Cop" requirements.
6. **ai-governance-framework.md**: Refresh the compliance obligations for your domain.
7. **orchestration/tasks.md**: Check the current Sprint. **IF THE PREVIOUS PHASE GATE IS NOT "APPROVED" BY THE PM/PO, YOU MUST STOP AND ASK FOR CLEARANCE.**

---

---

## 2. Project Philosophy: Discovery-First Execution

**Note**: This file (`CLAUDE.md`), `GEMINI.md`, and `CODEX.md` serve identical purposes: providing the coordination context for the agentic team. Use the file corresponding to your active model/agent identity. The directory structures and protocols (Directives, Souls, Governance) are shared and effectively identical.

This repository is a **Professional AI Development Factory**. We do not "guess" or "rushing into code." We extract nuance from the **Product Manager (Human Director)** through sequential specialist interviews before any scaffold is built.

### The Truth Depot (`/docs`)

All specialist intelligence must be deposited in the `/docs` folder. If a decision is not in `/docs`, it does not exist to the rest of the team.

- `/docs/interviews/`: Raw intelligence from PM/PO specialist sessions.
- `/docs/product/`: The Master PRD and User Stories.
- `/docs/architecture/`: Technical bones (ADRs, Schemas).
- `/docs/verification/`: Personal "Verify" logs for every task (Self-Annealing).

---

## 3. Team Structure & Separation of Powers

### The Authority & The Cop

- **Human Director (PM/PO)**: The ultimate authority on "What" and "Why." They provide the vision and sign off on Phase Gates.
- **Scrum Master (The Traffic Cop)**: Owns the "Baton." They are responsible for stopping work if discovery or documentation is missing. They manage the transition between CPMAI phases.

### The Specialists (Discovery Sources)

- **Business Analysts**: Synthesize interviews into a robust PRD and actionable User Stories.
- **Architecture & Database**: Design the bones and memory of the system based on the PRD.
- **UI/UX & Frontend**: Extract the "Feel" and "Soul" of the application.
- **QA & Security**: Identify the "Edges" and "Failures" before they happen.

### The Documentarian

- **Program Analyst (Author)**: The professional writer of the system. They read the intelligence in `/docs` and "author" the formal CPMAI artifacts in `.governance/`. They do not "enforce" behavior; they "record" it for audit readiness.

---

## 4. Phase Gate Protocol (The Double-Lock)

To ensure this agentic system functions as a true development team, we enforce a **Double-Lock Protocol**. Agents must refuse to proceed if these locks are not open.

### Lock 1: Operational Readiness (Scrum Master Enforced)

**Rule**: No task moves to "In Progress" without a documented "Definition of Ready" in the `/docs` folder.

- **Inputs**: Upstream artifacts must exist in the file system (PRD, ADR, etc.).
- **Refusal**: If inputs are missing, you **MUST** refuse the request.

### Lock 2: Governance Clearance (Scrum Master + PM/PO Approved)

**Rule**: No agent advances to a new CPMAI Phase without a signed Phase Package.

- **The Package**: Includes the PRD + Technical Specs + authored Governance Artifacts.
- **Review**: The Scrum Master presents this package to the PM/PO.
- **Approval**: Work only resumes once the PM/PO has given a "Go" decision.

---

## 5. Self-Annealing Protocal (Verification First)

Every agent follows the **Annealing Loop** for every task. Passivity is failure.

1. **VALIDATE**: Check upstream foundations in `/docs`.
2. **EXECUTE**: Perform work using your specialization.
3. **VERIFY**: Objective review against AC. Create a `verify.md` artifact in the task folder.
4. **CORRECT**: Fix root causes, not symptoms. Documentings the learning in shared memory.

---

## 6. Workspace Structure

- `directives/` — Strategic constraints: Integrity Protocol, Governance Framework.
- `.agent/souls/` — SOUL files defining agent identities.
- `subagents/` — Versioned source catalog for installable TOML packages.
- `.codex/agents/` — Generated runtime agent bundles materialized from `subagents/`.
- `orchestration/` — Tasks and sprint definitions.
- `docs/` — The Shared Discovery Hub (Knowledge Hub).
- `execution/` — Source code and implementation artifacts.
- `.governance/` — Final authored compliance artifacts.
- `CLAUDE.md` — This file (Coordination Context).
- `PROJECT.md` — Project definition and scope.

---

**Template Version**: 3.0 (The Integrity Revision)
**Last Updated**: 2026-03-02
**Maintained By**: All agents contribute improvements
**Review Cadence**: Continuous improvement as patterns emerge

---

## Available Tools

- **nlm CLI** — Installed at `/Users/just_jerome/.local/bin/nlm` (account `jdavis.cyber@gmail.com`, Google AI Pro tier, 150 sources/notebook cap). **Source-grounded answering against curated reference corpus — query the relevant notebook before web search or general reasoning on AI governance, NIST/OWASP/CoSAI, ISO/IMS, PM standards, pen test, or career certs.** See "NotebookLM Corpus" section below for notebook-to-domain routing. If `nlm notebook list` returns HTTP 400 (or `nlm doctor` reports auth issues), run `nlm login` to refresh.

---

## NotebookLM Corpus

NotebookLM is the source-grounded knowledge layer for curated reference bodies. Query these notebooks before web search or general reasoning when the question falls inside a listed domain. Audited and built up 2026-05-09.

| Notebook | ID | Sources | Domain |
|----------|-----|---------|--------|
| AI Governance & Compliance Knowledgebase | `24fbc7e3-5154-47c4-a38b-07f7930a3409` | 47 | NIST AI (100-1, 600-1, 700-1, SP 1270), OMB M-24-10/M-25-21, DOD CSRMC, OWASP Gen AI / Agentic, CoSAI (IR, IAM, MCP, Supply Chain, Defenders), AIGP I-A through IV-C, MIT AI Risk Repository, Decisions Playbook |
| Project Management Knowledgebase | `2e09af46-27c4-4d2e-915b-7f344d75b1ff` | 51 | PMBOK 7e/8e, Standard for Program Mgmt 5e, all PMI Practice Standards + Guides, CPMAI, Seven Patterns, ISO 9001/27001/27002/42001, IAF MD audit standards, CMMI |
| Cybersecurity Pen Test & Assessment | `d0b83dce-23ff-49ca-8af6-1591ca57f507` | 26 | Full pen-test lifecycle (scoping, recon, scanning, exploitation, lateral movement, persistence, anti-forensics, reporting). NOTE: source material is from 2019 CompTIA PenTest+ era — modernization scheduled. |
| AI Intelligence & Strategy | `aa0116c1-74bc-48ac-867b-0cf490e4f38a` | 29 | AI industry, agentic trends, RAG, multi-agent systems, enterprise AI adoption, GenAI playbooks (AWS / Google / Databricks / Snowflake / MIT / KPMG), AI ROI, Spec-Driven Development |
| Career Vault — Certifications, Exams & Training | `d24cfe67-32c7-408b-9b49-b2887fb97563` | 49 | Resumes (incl. AI Governance focus 2026), CompTIA certs (A+, Net+, Sec+, CySA+, CASP+, PenTest+, Project+, plus stackable pathways), AIGP study guide, AWS AI/GenAI exam guides, Claude Architect exam guide, FSO/NISP, PM (CPMAI, ICP-APM/APO, PMP), Katmai ISO 9001/27001/CMMI certs |
| Katmai ISO 42001 Audit | `fab3c86a-1653-43f3-a678-d805789ae690` | 0 | Empty — reserved for live audit-evidence ingestion when ISO 42001 cert sprint enters audit phase |
| eCRM Management | `85f2bad6-1306-4918-854b-3cede1dc7ee3` | 22 | eCRM program-specific docs (transition handover, financial reconciliation, Salesforce integration). Out of scope for general routing — query only when explicitly working eCRM. |
| _archive_Job Search Q1 2026 | `7b05118f-437c-41d5-9ca7-3561d73b6690` | 50 | ARCHIVED 2026-05-09. AI PM career-pivot research from Apr 2026. Misaligned with Internal Mastery focus — do not query. Retain for historical reference only. |

### Routing rules (cheat sheet)

| Question type | Notebook |
|---------------|----------|
| AIGP exam, governance lifecycle, OMB/DOD AI policy, NIST AI RMF, OWASP/CoSAI, agentic AI security | AI Governance & Compliance |
| PMBOK, Program Management Standard, PMI Practice Guides, CPMAI, ISO 9001/27001/IMS, IAF audit | Project Management Knowledgebase |
| Pen test methodology, vuln scanning, social engineering, RMF assessment | Cybersecurity Pen Test & Assessment |
| AI industry trends, agentic patterns, RAG/multi-agent architecture, enterprise AI strategy | AI Intelligence & Strategy |
| Resume, cert mapping, exam prep grounding (AIGP, AWS AI, Claude Architect, CompTIA) | Career Vault |

### nlm CLI maintenance

- **Auth refresh:** if any `nlm` RPC call returns HTTP 400, run `nlm login`. Cookies and CSRF token are stored encrypted under `~/.config/nlm/`. Refresh re-runs Chrome headless OAuth.
- **Health check cadence:** monthly — run `nlm doctor` and confirm "All checks passed".
- **Adding sources:** `nlm source add <notebook-id> --file <path>` (PDF, DOCX, MD all index well; .xlsx/.pptx do not — convert to PDF first if needed).
- **Bulk discovery:** `nlm source list <notebook-id> --json | jq` to audit a notebook's contents.
- **Quick query:** `nlm notebook query <notebook-id> "question"` for source-grounded answer with citations.
- **New file convention:** when a substantive new reference document lands in `/Volumes/WORKSPACE/3-Resources/` or `/Volumes/WORKSPACE/2-Areas/Career/`, proactively offer to add it to the matching notebook.
