# DoW AI PM Builder — Demo Runbook

Two scripted walkthroughs: a 15-minute **auditor demo** (ISO/IEC 42001
certification body) and a 10-minute **executive demo** (Director / COO).
This system's demo is its *governance operating*, not an app screen —
lean into that.

---

## Pre-Demo Checklist (night before)

- [ ] Fresh clone on the demo machine; follow `INSTALL.md` exactly —
      any friction found is a doc bug to fix tonight
- [ ] `bash automation/install-subagents.sh` ran; `.codex/agents/runtime-manifest.json` exists
- [ ] `python3 automation/validate_spec.py orchestration/system_spec.md` → PASSED
- [ ] Terminal tabs ready: repo root in an editor/file tree, one shell,
      `git log --oneline -15`
- [ ] Skim `.agent/souls/security-compliance-officer.md` — you will open it live

---

## The Premise (say this first, both audiences)

> "Most AI coding assistants are a single brilliant intern with no rules.
> This is a **governed software factory**: fifteen specialized agents with
> separated duties, phase gates that fail closed, and a compliance officer
> with veto power. The output isn't just software — it's software **plus the
> audit-ready evidence trail** that regulated delivery demands."

---

## Auditor Demo (15 min) — "Governance that machines enforce"

### 1. Separation of duties, in files (4 min)
- Open `.agent/souls/` — fourteen immutable agent identities. Open the
  Security & Compliance Officer SOUL: she audits, she does not build.
- Open `directives/` — the constitution every agent must read before acting.
- Key line: "Agent behavior is version-controlled. A change to an agent's
  authority is a git commit, reviewable and revertible — change management
  on the AI itself."

### 2. Fail-closed phase gates (4 min)
- Walk `CLAUDE.md` → Double-Lock protocol: Lock 1 operational readiness,
  Lock 2 governance clearance. Nothing proceeds on a missing artifact.
- Open `.governance/` — phase-gate records and the Override Register
  concept: deviation is possible but *documented and attributable*, never
  silent.
- Run live: `python3 automation/validate_spec.py orchestration/system_spec.md`
  — "the spec lint is fail-closed: TBDs block the factory from starting.
  This is a machine-enforced Definition of Ready."

### 3. CPMAI + multi-framework mapping (4 min)
- Phase gates align to CPMAI phases; compliance scopes declared in
  `subagents/install-config.json` (CMMC 2.0, FedRAMP, ISO 42001).
- "One engagement produces evidence reusable across frameworks — the
  cross-mapping is an artifact, not an afterthought."

### 4. The AIMS bridge (3 min)
- "For ISO 42001: this is the organization's controlled process for
  *developing* AI-augmented systems. The AIMS governs AI; this is what
  governed AI development looks like in operation — roles, gates,
  documented overrides, evidence by default."

---

## Executive Demo (10 min) — "Compliant delivery, industrialized"

### 1. The hook (2 min)
- Premise, then: "Regulated software delivery is slow because compliance is
  manual and retrospective. This factory makes it automatic and continuous —
  the evidence package builds itself as the work happens."

### 2. The walkthrough (5 min)
- The roster (15 agents, 136 specializations) — "a full delivery team's
  separation of duties, at AI cost and speed."
- The Double-Lock gate — "nothing ships on a hunch; your risk posture is
  enforced by the system, not by hoping people follow the SOP."
- The spec validator run — one command, instant fail-closed quality gate.

### 3. The strategic frame (3 min)
- "This is a capability multiplier: every new engagement starts from a
  governed baseline instead of a blank page. Combined with ISO 42001
  certification, it's a market differentiator — we can demonstrate *how*
  our AI-assisted delivery is controlled, not just claim it."

---

## Q&A Preparation

| Likely question | Answer |
|---|---|
| "Is the AI making decisions unsupervised?" | No — a Human Director holds final authority at every phase gate; agents prepare, humans approve. Overrides are logged and attributable. |
| "What if an agent goes off-script?" | Directives are mandatory startup reading; the spec validator and gate locks fail closed; deviations require an Override Register entry. |
| "What does it cost?" | The template is internal IP. Marginal cost is AI inference per engagement — a fraction of the equivalent staff-hours it offsets. |
| "Has it built anything real?" | Yes — it has run Sprint Zero discovery through Gate 1 on a real LMS requirement set, producing the PRD, stories, ADRs, and gate evidence this process defines. |
| "How does this relate to ISO 42001?" | It is operating evidence: a controlled, auditable process for AI-assisted development — exactly what an AIMS expects to see governing AI use in delivery. |
