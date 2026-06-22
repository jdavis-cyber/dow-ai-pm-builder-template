# Complete Agent Roster — 15 Accountable Agents

This is the authoritative roster for the DoW AI PM Builder Template. The factory is a **15-agent governed scrum team**. The 136 VoltAgent packages under `subagents/global/voltagent/` are specialization/capability packages, not accountable peer agents.

## Roster Consistency Rule

- `.agent/souls/` must contain exactly these 15 SOUL files.
- `subagents/install-config.json` must install these same 15 accountable agents by default.
- `.codex/agents/runtime-manifest.json` must materialize these same 15 accountable agents before work begins.
- Security & Compliance Officer is mandatory in every generated project.

## Thinkers (4 accountable agents)

### Requirements BA
**Accountable Agent ID**: `requirements-ba`  
**SOUL File**: `.agent/souls/requirements-ba.md`  
**Runtime Package**: `subagents/.../requirements-ba.toml`  
**Primary Accountability**: Business requirements elicitation and measurable outcomes.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### User Story BA
**Accountable Agent ID**: `user-story-ba`  
**SOUL File**: `.agent/souls/user-story-ba.md`  
**Runtime Package**: `subagents/.../user-story-ba.toml`  
**Primary Accountability**: User stories, acceptance criteria, and traceability.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### UI/UX Designer
**Accountable Agent ID**: `ui-ux-designer`  
**SOUL File**: `.agent/souls/ui-ux-designer.md`  
**Runtime Package**: `subagents/.../ui-ux-designer.toml`  
**Primary Accountability**: User experience, interaction design, and accessibility intent.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Architecture SE
**Accountable Agent ID**: `architecture-se`  
**SOUL File**: `.agent/souls/architecture-se.md`  
**Runtime Package**: `subagents/.../architecture-se.toml`  
**Primary Accountability**: System architecture and technical decisions.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

## Builders (5 accountable agents)

### Database Engineer
**Accountable Agent ID**: `database-engineer`  
**SOUL File**: `.agent/souls/database-engineer.md`  
**Runtime Package**: `subagents/.../database-engineer.toml`  
**Primary Accountability**: Data modeling, schemas, and persistence design.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Backend Developer
**Accountable Agent ID**: `backend-developer`  
**SOUL File**: `.agent/souls/backend-developer.md`  
**Runtime Package**: `subagents/.../backend-developer.toml`  
**Primary Accountability**: Server-side APIs, integrations, and business logic.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Frontend Developer
**Accountable Agent ID**: `frontend-developer`  
**SOUL File**: `.agent/souls/frontend-developer.md`  
**Runtime Package**: `subagents/.../frontend-developer.toml`  
**Primary Accountability**: Client-side implementation and UI integration.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Pipeline DevOps
**Accountable Agent ID**: `pipeline-devops`  
**SOUL File**: `.agent/souls/pipeline-devops.md`  
**Runtime Package**: `subagents/.../pipeline-devops.toml`  
**Primary Accountability**: CI/CD, deployment automation, and release controls.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Performance DevOps
**Accountable Agent ID**: `performance-devops`  
**SOUL File**: `.agent/souls/performance-devops.md`  
**Runtime Package**: `subagents/.../performance-devops.toml`  
**Primary Accountability**: Performance, monitoring, and capacity engineering.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

## Critics (2 accountable agents)

### QA Engineer
**Accountable Agent ID**: `qa-engineer`  
**SOUL File**: `.agent/souls/qa-engineer.md`  
**Runtime Package**: `subagents/.../qa-engineer.toml`  
**Primary Accountability**: Functional, exploratory, and acceptance testing.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Automation Test Engineer
**Accountable Agent ID**: `automation-test-engineer`  
**SOUL File**: `.agent/souls/automation-test-engineer.md`  
**Runtime Package**: `subagents/.../automation-test-engineer.toml`  
**Primary Accountability**: Regression automation and executable test gates.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

## Governance & Compliance (4 accountable agents)

### Scrum Master
**Accountable Agent ID**: `scrum-master`  
**SOUL File**: `.agent/souls/scrum-master.md`  
**Runtime Package**: `subagents/.../scrum-master.toml`  
**Primary Accountability**: Traffic-cop coordination, dependency, and phase-gate enforcement.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Program Analyst
**Accountable Agent ID**: `program-analyst`  
**SOUL File**: `.agent/souls/program-analyst.md`  
**Runtime Package**: `subagents/.../program-analyst.toml`  
**Primary Accountability**: Governance evidence authoring and management-system artifacts.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.
**Boundary**: Authors and maintains governance evidence and management-system artifacts; does not waive compliance gates.

### Documentation SE
**Accountable Agent ID**: `documentation-se`  
**SOUL File**: `.agent/souls/documentation-se.md`  
**Runtime Package**: `subagents/.../documentation-se.toml`  
**Primary Accountability**: Technical documentation, handoff, and knowledge management.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.

### Security & Compliance Officer
**Accountable Agent ID**: `security-compliance-officer`  
**SOUL File**: `.agent/souls/security-compliance-officer.md`  
**Runtime Package**: `subagents/.../security-compliance-officer.toml`  
**Primary Accountability**: Mandatory security/compliance gate enforcement and override register control.
**Mandatory Runtime**: Yes — installed by `subagents/install-config.json` v2.
**Boundary**: Enforces compliance gates, fail-closed findings, and override register requirements; does not replace the Program Analyst.

---

## Typical Workflow Sequence

1. **Sprint Zero / Discovery** — Requirements BA, User Story BA, UI/UX Designer, Architecture SE, Database Engineer, QA Engineer, Automation Test Engineer, Program Analyst, Scrum Master, and Security & Compliance Officer establish the Definition of Ready and evidence plan.
2. **Design & Planning** — Architecture SE, Database Engineer, UI/UX Designer, Program Analyst, Documentation SE, Scrum Master, and Security & Compliance Officer confirm design, standards applicability, and gate evidence.
3. **Implementation** — Backend Developer, Frontend Developer, Pipeline DevOps, Performance DevOps, QA Engineer, and Automation Test Engineer build only against approved inputs.
4. **Verification** — QA Engineer and Automation Test Engineer run executable checks; Documentation SE and Program Analyst index evidence; Security & Compliance Officer reviews compliance evidence.
5. **Phase Gate** — Scrum Master coordinates the gate. Program Analyst presents management-system evidence. Security & Compliance Officer participates at every gate and fails closed if evidence is unavailable or an override is missing.

## Specialization Boundary

VoltAgent TOMLs may be activated as execution lenses by accountable owners. They cannot weaken SOUL duties, phase gates, fail-closed controls, or evidence obligations.
