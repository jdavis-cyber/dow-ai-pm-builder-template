# Factory Statement of Applicability — ISO/IEC 42001 Annex A & NIST AI RMF

**Scope and honesty statement (read first).** This is the reverse sweep to the
forward control matrix (`factory-control-matrix.md`): every ISO/IEC 42001:2023
Annex A control (A.2–A.10) and every NIST AI RMF 1.0 category receives an
explicit disposition for the factory *itself* — applicable or not, and if
applicable whether it is met, partially met, or a gap. It is a **repo-level
self-assessment**, **not a certification claim**, and it is distinct from any
organization-level Statement of Applicability an adopter maintains: clauses
that require an operating organization (leadership, competence, internal
audit, management review) attach to the adopter, and this document supplies
the factory-level control layer beneath them. Control numbers and titles were
cited from the source standards via source-grounded corpus lookup on
2026-07-10 — no from-memory citations. Conditional product/engagement
overlays (CMMC, NIST SP 800-171, FedRAMP, HIPAA, SOC 2) are deliberately
absent per `directives/factory-governance-scope.md`.

**Status legend:** ✅ Met (mechanism exists and is verifiable) · ◐ Partial
(mechanism exists but incomplete at template scope; rationale given) ·
**N/A** (not applicable; justification given). Every ◐ row carries an
accepted-gap rationale or a tracking reference — nothing is left implicit.

## The AI system under assessment — factory categorization (NIST AI RMF MAP 2)

- **Task definition (MAP 2.1):** a multi-agent orchestration template that
  uses supplier **generative models** (LLMs), via provider-neutral shell
  adapters, to produce project-management and software artifacts. The factory
  trains no models, hosts no endpoints, and performs no automated decisioning
  about individuals.
- **System limits and human oversight (MAP 2.2):** knowledge limits are the
  supplier model's; the factory compensates structurally — outputs are Draft
  until human-gated, and the Human Director holds every consequential
  authority (phase-gate approval, implementation, deployment, external
  writes, risk acceptance, control closure) through a fail-closed authority
  store (`.governance/gate_state.json`, `automation/gatekeeper.py`). Human
  oversight points: Sprint Zero interview → Lock 0 spec validation → per-task
  dispatch packets → post-dispatch detective stops → phase gates 1–6 with a
  mandatory Security & Compliance Officer review.
- **TEVV and scientific integrity (MAP 2.3):** the control set itself is
  executable — whole-template validation, golden-path smoke test, and the
  governance regression suite run locally and in CI on every change
  (`.github/workflows/validate.yml`).
- **Autonomy level:** bounded task-level autonomy. An adapter may execute one
  scoped task packet autonomously; it cannot advance phases, acquire
  authority, or self-redispatch (open-task redispatch guard).

## ISO/IEC 42001:2023 Annex A — per-control disposition

### A.2 Policies related to AI

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.2.2 | AI policy | Yes | ✅ | `factory-ai-policy.md` — policy for the factory's own AI use |
| A.2.3 | Alignment with other organizational policies | Yes | ✅ | `factory-ai-policy.md` §Alignment — defers to SECURITY.md, scope directive, licenses, and the adopter's policies |
| A.2.4 | Review of the AI policy | Yes | ✅ | `factory-ai-policy.md` §Review cadence — every version bump and at least annually, staleness detectable via the verification stamp |

### A.3 Internal organization

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.3.2 | AI roles and responsibilities | Yes | ✅ | 15-agent accountable roster with written mandates; Security & Compliance Officer non-removable (`.agent/souls/`, `subagents/install-config.json`) |
| A.3.3 | Reporting of concerns | Yes | ✅ | Override register (recorded exceptions), escalation template (`orchestration/escalation-template.md`), SECURITY.md private reporting path |

### A.4 Resources for AI systems

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.4.2 | Resource documentation | Yes | ✅ | README, INSTALL.md, runtime manifest (`.codex/agents/runtime-manifest.json`), `factory.config.example.json` |
| A.4.3 | Data resources | **N/A** | — | The factory uses no datasets: it consumes operator-supplied project text per session and trains nothing. If a generated product uses data, A.7/A.4.3 attach to that product via the overlay doctrine |
| A.4.4 | Tooling resources | Yes | ✅ | 156-entry specialization ownership map; every vendored tool owner-mapped (`subagents/specialization-ownership-map.json`) |
| A.4.5 | System and computing resources | Yes | ✅ | INSTALL.md (Python, git, provider CLI requirements); local on-demand operation, no persistent infrastructure |
| A.4.6 | Human resources | Yes | ◐ | The Human Director role and interview protocol are defined (`KICKOFF.md`, `directives/director-interview-protocol.md`); operator *competence* management is organization-level (clause 7.2) — **accepted gap at template scope, attaches to adopter** |

### A.5 Assessing impacts of AI systems

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.5.2 | AI system impact assessment process | Yes | ✅ | Mission risk profile required at Gate 1 (`.governance/Phase_Gates/Gate1_BusinessUnderstanding/`); factory-level risks in `factory-risk-register.md` |
| A.5.3 | Documentation of AI system impact assessments | Yes | ✅ | Gate 1 records persist in `.governance/Phase_Gates/`; the factory risk register is versioned in-repo |
| A.5.4 | Assessing AI system impact on individuals or groups | Yes | ◐ | The factory performs no automated decisioning about individuals; bias risk is registered (FR-03) and human-gated but not measured. Full individual-impact assessment is an adopter AIA artifact — **accepted gap at template scope** |
| A.5.5 | Assessing societal impacts of AI systems | Yes | ◐ | Registered at factory level (workforce/skill-shift concerns acknowledged in the adopter's AIA); no standalone societal-impact analysis ships in-repo — **accepted gap: attaches to the adopter's impact assessment** |

### A.6 AI system life cycle

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.6.1.2 | Objectives for responsible development of AI system | Yes | ✅ | `factory-objectives.md` — measurable objectives with thresholds and owners |
| A.6.1.3 | Processes for responsible AI system design and development | Yes | ✅ | Double-Lock governance, CPMAI phase gates, structural-integrity protocol (`directives/structural-integrity-protocol.md`) |
| A.6.2.2 | AI system requirements and specification | Yes | ✅ | System spec + Lock 0 validation (`orchestration/system_spec.md`, `automation/validate_spec.py`) |
| A.6.2.3 | Documentation of AI system design and development | Yes | ✅ | `docs/architecture/`, decision records (`docs/decisions/`), CHANGELOG |
| A.6.2.4 | AI system verification and validation | Yes | ✅ | Validation gauntlet + CI (`automation/validate_template.py`, `smoke_test_template.py`, `tests/`) |
| A.6.2.5 | AI system deployment | Yes | ✅ | Deployment authority ships denied in the fail-closed store; explicit human grant required (`.governance/gate_state.json`) |
| A.6.2.6 | AI system operation and monitoring | Yes | ✅ | Post-dispatch detective stops; run-result records; `factory_metrics.py` aggregation |
| A.6.2.7 | AI system technical documentation | Yes | ✅ | Audience-differentiated docs: README (adopters), KICKOFF (operators), directives (agents), docs tree (auditors) |
| A.6.2.8 | AI system recording of event logs | Yes | ✅ | Task packets + run-result records per autonomous dispatch (`docs/verification/factory-runs/`); git history for all artifact changes |

### A.7 Data for AI systems

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.7.2 | Data for development and enhancement of AI system | **N/A** | — | The factory develops no models and holds no development datasets. Overlay doctrine applies if a generated product does (`directives/factory-governance-scope.md`) |
| A.7.3 | Acquisition of data | **N/A** | — | No data acquisition: operator-supplied project context only, per session |
| A.7.4 | Quality of data for AI systems | **N/A** | — | No datasets to quality-manage; input quality is handled as spec quality (Lock 0), not data quality |
| A.7.5 | Data provenance | **N/A** | — | No datasets; provenance obligations for *vendored content* are met separately (THIRD_PARTY_LICENSES.md, ownership map) |
| A.7.6 | Data preparation | **N/A** | — | No data preparation pipeline exists |

### A.8 Information for interested parties of AI systems

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.8.2 | System documentation and information for users | Yes | ✅ | README (incl. Known limitations), INSTALL.md, KICKOFF.md |
| A.8.3 | External reporting | Yes | ✅ | SECURITY.md private vulnerability reporting; GitHub issues for non-sensitive reports |
| A.8.4 | Communication of incidents | Yes | ✅ | SECURITY.md §Incident communication — advisory + CHANGELOG + in-repo correction; no-push-channel limitation stated |
| A.8.5 | Information for interested parties | Yes | ◐ | Attribution and licensing obligations met (THIRD_PARTY_LICENSES.md, LICENSE); formal reporting obligations to regulators/customers are adopter-level — **accepted gap at template scope** |

### A.9 Use of AI systems

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.9.2 | Processes for responsible use of AI systems | Yes | ✅ | Provider startup protocol (CLAUDE/CODEX/GEMINI, byte-identical), stop conditions, fail-closed rule |
| A.9.3 | Objectives for responsible use of AI system | Yes | ✅ | `factory-objectives.md` (FO-1..FO-5 govern use, not just development) |
| A.9.4 | Intended use of the AI system | Yes | ✅ | Two-track scope doctrine + claims-integrity fence keep the factory inside its intended use; authority store blocks out-of-scope actions |

### A.10 Third-party and customer relationships

| Control | Title | Applicable | Status | Evidence / justification |
|---------|-------|------------|--------|--------------------------|
| A.10.2 | Allocating responsibilities | Yes | ✅ | Ownership map allocates every capability to an accountable role; GOVERNANCE_WRAPPER defines precedence |
| A.10.3 | Suppliers | Yes | ✅ | `model-supplier-criteria.md` (runtime providers) + THIRD_PARTY_LICENSES.md and Dependabot (vendored/CI supply chain) |
| A.10.4 | Customers | Yes | ◐ | The template's "customers" are adopters: needs addressed via README/KICKOFF/INSTALL. No formal customer-expectation process exists — **accepted gap: a template has users, not customer relationships; attaches to the adopter's engagement** |

## NIST AI RMF 1.0 — per-category disposition

| Category | Statement (abbrev.) | Status | Evidence / justification |
|----------|--------------------|--------|--------------------------|
| GOVERN 1 | Policies, processes, procedures in place and implemented | ✅ | Fail-closed authority store, dispatch packets, evidence index, versioned change record (matrix rows 6, 7, 10, 14) |
| GOVERN 2 | Accountability structures in place | ✅ | Accountable roster + ownership map (matrix rows 1–2) |
| GOVERN 3 | Workforce diversity, equity, inclusion prioritized | — | **Intentionally unmapped:** organizational workforce function; no factory-level mechanism, not stretched (accepted gap, also stated in the control matrix) |
| GOVERN 4 | Culture that considers and communicates AI risk | ✅ | Override register (exceptions are visible events), claims-integrity fence, honest known-limitations documentation |
| GOVERN 5 | Engagement with relevant AI actors | — | **Intentionally unmapped:** external-engagement is an organizational function (accepted gap, also stated in the control matrix) |
| GOVERN 6 | Third-party software/data supply-chain policies | ✅ | Ownership map, THIRD_PARTY_LICENSES.md, supplier criteria, Dependabot |
| MAP 1 | Context established and understood | ✅ | Sprint Zero discovery interview + Lock 0 (matrix row 3) |
| MAP 2 | Categorization of the AI system performed | ✅ | §Factory categorization above (task definition, oversight points, TEVV) |
| MAP 3 | Capabilities, usage, benefits/costs vs benchmarks | ◐ | Capabilities and intended usage documented (README, this file); no cost/benefit benchmark data at template scope — **accepted gap: benchmarks require operational runs; FO-2/FO-3 metrics accumulate the data once runs exist** |
| MAP 4 | Risks mapped for all components incl. third-party | ✅ | Factory risk register (FR-01..FR-17) + third-party attribution/ownership |
| MAP 5 | Impacts characterized | ✅ | Mission risk profile at Gate 1; register rows FR-03/FR-06/FR-09 |
| MEASURE 1 | Appropriate methods and metrics identified/applied | ✅ | Validation gauntlet + CI + `factory_metrics.py` |
| MEASURE 2 | Systems evaluated for trustworthy characteristics | ◐ | Validity/reliability covered by the gauntlet; bias and explainability are not measured at factory level — **accepted gap: measurement attaches to a generated product with real usage (register FR-03)** |
| MEASURE 3 | Mechanisms for tracking identified risks over time | ✅ | Run-result records + risk register review cadence (matrix row 8) |
| MEASURE 4 | Feedback on measurement efficacy gathered | ✅ | CI history + version-bump review of validator efficacy (matrix row 11); validator changes recorded in CHANGELOG |
| MANAGE 1 | Risks prioritized, responded to, managed | ✅ | Phase gates with mandatory Security & Compliance Officer review (matrix row 5) |
| MANAGE 2 | Benefit-maximization strategies planned/documented | ◐ | Objectives define targets and thresholds; formal benefit-realization tracking needs operational data — **accepted gap until runs accumulate (same basis as MAP 3)** |
| MANAGE 3 | Third-party risks managed | ✅ | Supplier criteria + provider-neutral fallback + attribution/ownership (matrix rows 2, 12) |
| MANAGE 4 | Risk treatments documented and monitored; response/recovery/communication plans | ✅ | Detective stops + run results (matrix row 8), override register, SECURITY.md incident communication |

## Known gaps — consolidated

Every non-✅ disposition above is one of:

1. **Adopter-attached** (A.4.6, A.5.4, A.5.5, A.8.5, A.10.4): requires an
   operating organization, an engagement, or real affected users. The factory
   ships the operational layer; the adopter's management system completes it.
2. **Operationally-gated** (MAP 3, MEASURE 2, MANAGE 2): requires accumulated
   run data or product-level usage that a pristine template cannot have.
   `factory_metrics.py` is the accumulation mechanism.
3. **Intentionally unmapped** (GOVERN 3, GOVERN 5): organizational functions
   with no honest factory-level mechanism; stretching them would violate the
   claims-integrity fence.

No Annex A control and no RMF category is silently omitted.

*Maintained by: Human Director. Update this SoA in the same change that adds,
removes, or weakens any mechanism it cites. Verified against commit `8991e57`
(2026-07-10); re-verify at every version bump.*
