# Agent Activation Matrix

**Authority**: `orchestration/system_spec.md` Section A (Project Classification Inputs)
**Purpose**: Phase 0 control-plane reference for which runtime packages the installer may materialize into `.codex/agents/`
**Update Date**: 2026-03-30

---

## Operational Model: Source-Catalog to Generated-Runtime

This template uses a **two-tier packaging model** to enforce deterministic, auditable agent activation:

### Source Catalog (`subagents/`)

The **source catalog** contains versioned, reviewed master TOML definitions for all available agent packages. Each TOML defines an agent's identity, capabilities, governance constraints, and dependencies.

**Location**: `subagents/` directory (organized by activation tier)
```
subagents/
├── global/          # Activated on every project
│   ├── scrum-master.toml
│   ├── program-analyst.toml
│   ├── documentation-se.toml
│   └── pipeline-devops.toml
└── dod-regulated/   # Activated only for regulated projects
    └── security-compliance-officer.toml
```

**Key Property**: Source TOMLs are **static, reviewed, and never modified in response to runtime failures**. If a TOML is wrong, the source is updated and versioned—the runtime does not improvise.

### Generated Runtime (`.codex/agents/`)

The **generated runtime** is materialized by the installer when a project is initialized. It contains only the runtime bundles appropriate for the project's classification profile.

**Location**: `.codex/agents/runtime-manifest.json` + actual TOML bundles
**Key Property**: Runtime bundles are **read-only during execution**. Agents use the runtime bundles, not the source catalog.

**Example**: A `dod-regulated` project will have both `program-analyst` and `security-compliance-officer` bundles in the runtime. A `standard` project will have only the global set.

---

## Fail-Closed Control-Plane Behavior

**The Golden Rule**: If something is missing, unknown, or contradictory during startup, the system **fails fast and asks for help rather than improvising**.

### Fail-Closed Triggers

1. **Missing Source TOML**: If the installer references a package that doesn't exist in `subagents/`, installation stops with an error (not a missing-file warning).
2. **Unknown Package Name**: Any package listed in `install-config.json` that is not in the activation matrix is an error (not a typo to be guessed at).
3. **Classification Conflict**: If `project_type` or profile traits contradict the classification decision rules (see below), installation stops and the Scrum Master must re-open discovery.
4. **Missing Runtime Manifest**: If `.codex/agents/runtime-manifest.json` is not present or is malformed after install, runtime agents refuse to start and escalate to the installer.

**Audit Implication**: Every startup failure leaves a traceable record and must be explicitly resolved before execution resumes.

---

## Agent Activation Matrix

| Package | Tier | Default | Activate When | Source TOML | Control Objective |
| --- | --- | --- | --- | --- | --- |
| `scrum-master` | `global` | Yes | Every initialized project | `subagents/global/scrum-master.toml` | Double-Lock enforcement and escalation control |
| `program-analyst` | `global` | Yes | Every initialized project | `subagents/global/program-analyst.toml` | Governance artifact authorship and audit traceability |
| `documentation-se` | `global` | Yes | Every initialized project | `subagents/global/documentation-se.toml` | Documentation control and truth-depot hygiene |
| `pipeline-devops` | `global` | Yes | Every initialized project | `subagents/global/pipeline-devops.toml` | Installer, telemetry, and deployment control surfaces |
| `security-compliance-officer` | `dod-regulated` | No | `project_type` is `dod-regulated` or `hipaa`, OR `requires_dod_controls` is true | `subagents/dod-regulated/security-compliance-officer.toml` | Regulated review gate for deployment and evidence changes |

---

## Phase 0 Activation Rules

### Rule 1: Install the `global` baseline on every project

Every initialized project receives the full `global` agent set. These agents enforce the Double-Lock protocol, capture governance evidence, maintain documentation integrity, and control deployment.

**Effect**: `orchestration/system_spec.md` Section A must be approved before any project initialization.

### Rule 2: Install `dod-regulated` agents only when the classification profile requires them

Regulated overlay agents (e.g., `security-compliance-officer`) are activated only when:
- `project_type` is explicitly `dod-regulated` or `hipaa`, OR
- `requires_dod_controls` is `true`, OR
- `requires_iso42001` is `true`

**Effect**: Projects cannot self-add regulated overlays. The classification decision must come from the Human Director or Requirements BA during Sprint Zero.

### Rule 3: Never activate packages without explicit project selection

Unknown, unreviewed, or self-invented packages are not materialized into runtime, even if someone adds them to `install-config.json` manually.

**Effect**: All packages must exist in the source catalog (`subagents/`) and be listed in the activation matrix.

### Rule 4: Fail immediately if classification inputs are missing or contradictory

If `install-config.json` specifies invalid traits, if a required source TOML is missing, or if the project classification answers violate the decision rules below, the installer **stops and escalates** rather than choosing defaults.

**Effect**: The Scrum Master must review the blocker and either correct the inputs or re-open discovery with the Requirements BA.

---

## Classification Decision Rules

These rules enforce the tie between discovered project scope and selected runtime packages. They are enforced by the installer and by the Scrum Master at gate reviews.

| Decision | Rule |
|----------|------|
| **DoD Regulatory Scope** | If `project_type` is `dod-regulated`, then `requires_dod_controls` MUST be `true`. Conversely, if `requires_dod_controls` is claimed but `project_type` is not `dod-regulated`, installation stops and the Human Director must clarify scope. |
| **Regulated Overlay Activation** | If `requires_dod_controls` is `true`, the `security-compliance-officer` agent is mandatory. This agent is not optional. |
| **AI Project Scope** | If `project_type` is `ai-ml`, then `requires_iso42001` must be explicitly answered (true or false). It may not be inferred. |
| **Compliance Scope Authority** | The Human Director (not the installer, not the technical team) declares that the project is regulated. This scope must be recorded in `docs/product/project-classification-inputs.md` before any implementation work begins. |
| **Conflict Resolution** | If classification answers are internally contradictory (e.g., `project_type` is `standard` but `requires_dod_controls` is `true`), installation stops. The Scrum Master must re-open discovery rather than choosing a best-effort profile. |

---

## Startup Validation Protocol

Every agent verifies the runtime manifest on startup. This is a non-negotiable safety check.

### Startup Steps (Per CODEX.md / CLAUDE.md Step 3)

1. **Check for Runtime Manifest**: Is `.codex/agents/runtime-manifest.json` present?
   - ✅ **Present**: Parse and verify the manifest schema.
   - ❌ **Missing**: Fail with error "Runtime manifest not found. This is an installation error, not an agent configuration issue. Escalate to installer."

2. **Verify Package Installation**: For each package listed in the manifest, confirm the TOML is present.
   - ✅ **Present**: Load and validate the TOML structure.
   - ❌ **Missing**: Fail with error "Required package [name] is listed in manifest but TOML not found. This is an installation failure. Escalate to installer."

3. **Confirm Activation Eligibility**: For each loaded package, verify it is in the activation matrix.
   - ✅ **In Matrix**: Load the agent.
   - ❌ **Unknown Package**: Fail with error "Package [name] is not in the activation matrix. This may indicate a manual edit or an install error. Escalate to Scrum Master."

4. **Load All Required Agents**: After validation, load each activated agent into the runtime.
   - ✅ **All agents loaded**: Proceed to Phase Gate protocol check.
   - ❌ **Any agent fails to load**: Fail with error and list the failing agents. Do not partially start.

---

## Documentation Reference

For more information, see:
- **System Spec Section A**: `orchestration/system_spec.md` — Project classification answers and decision rules
- **Startup Protocol**: `CODEX.md` and `CLAUDE.md` Step 3 — Runtime manifest validation
- **Double-Lock Protocol**: `directives/structural-integrity-protocol.md` — Gate sequencing and escalation
- **Governance Framework**: `directives/ai-governance-framework.md` — Compliance scope and artifact contracts


---

## v4.0 Additions — Security Officer + New Specializations

### Security & Compliance Officer — Mandatory Phase Gate Activation

The Security & Compliance Officer (Agent 15) activates at every CPMAI Phase Gate:

| CPMAI Phase | Security Officer Actions |
|-------------|--------------------------|
| Phase 1 — Business Understanding | ISO/IEC 42001 Clauses 4-6 initiation audit; DoW CSRMC Mission Risk Profile start; regulatory applicability determination |
| Phase 2 — Data Understanding | Data classification audit (CUI/PII/PHI); DoD data handling requirements; initial privacy impact assessment |
| Phase 3 — Data Preparation | Data handling compliance verification; NIST SP 800-53 data control applicability; FedRAMP data boundary confirmation |
| Phase 4 — Model Development | AI bias assessment (NIST SP 1270); model card generation (ISO 42001 Annex A); NIST AI RMF MAP+MEASURE |
| Phase 5 — Model Evaluation | Full CMMC 2.0 assessment; complete RMF waterfall; ATO package initiation; SOC 2 evidence collection |
| Phase 6 — Operationalization | Final compliance certification; ISO/IEC 42001 full audit; ATO package completion; DoW CSRMC Automated Evidence Package |

### New Specialization Activations (v4.0)

| Specialization | Source | Phase Activation | Owner Agent |
|----------------|--------|-----------------|-------------|
| chaos-engineer | VoltAgent Tier 04 | Phases 4-5 | Automation Test Engineer |
| sre-engineer | VoltAgent Tier 03 | Phase 6 | Pipeline DevOps |
| terraform-engineer | VoltAgent Tier 03 | Phases 3, 6 | Pipeline DevOps |
| cloud-architect | VoltAgent Tier 03 | Phases 3, 6 | Pipeline DevOps |
| accessibility-tester | VoltAgent Tier 04 | Phases 4-5 | Frontend Developer / UI-UX Designer |
| context-manager | VoltAgent Tier 09 | All phases (persistent) | Scrum Master |
| architect-reviewer | VoltAgent Tier 04 | Phase 2 gate review | Architecture SE |
| llm-architect | VoltAgent Tier 05 | Phases 2, 4 | Architecture SE |
| api-designer | VoltAgent Tier 01 | Phase 3 | Architecture SE / Backend Developer |
| knowledge-synthesizer | VoltAgent Tier 09 | Phase Gates 5-6 | Documentation SE / Program Analyst |
| compliance-auditor | VoltAgent Tier 04 | All phase gates | Program Analyst |
| data-engineer | VoltAgent Tier 05 | Phase 3 | Database Engineer |
| terragrunt-expert | VoltAgent Tier 03 | Phase 6 | Pipeline DevOps |
| code-mapper | VoltAgent Tier 01 | Phases 3-4 | Documentation SE / Backend Developer |

