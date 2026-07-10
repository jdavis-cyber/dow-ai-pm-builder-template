# Factory Control Matrix — ISO/IEC 42001 & NIST AI RMF

**Scope and honesty statement (read first).** This matrix maps the factory's
*own* operating mechanisms — not the generated product's — to ISO/IEC
42001:2023 clauses/Annex A controls and NIST AI RMF 1.0 (NIST AI 100-1)
functions. It is a **repo-level self-assessment**: it demonstrates that each
mechanism exists, names the evidence that proves it operates, and states how
to verify it. It is **not a certification claim**, and it does not cover
organization-level requirements a management system also needs (top-management
commitment, internal audit program, management review, personnel competence).
Clause and category titles were cited from the source standards via
source-grounded corpus lookup on 2026-07-10. Frameworks that attach to the
operating *environment* (CMMC, NIST SP 800-171, FedRAMP) are conditional
product/engagement overlays per `directives/factory-governance-scope.md` and
are deliberately absent here.

Verification commands referenced below can be run by any auditor from a fresh
clone; CI (`.github/workflows/validate.yml`) runs them on every change.

| # | Factory mechanism | What it does | ISO/IEC 42001 | NIST AI RMF | Evidence | How to verify |
|---|---|---|---|---|---|---|
| 1 | Accountable-agent roster (15 mandatory roles; Security & Compliance Officer non-removable) | Every action resolves to a named, accountable role with written duties | 5.3 Roles, responsibilities and authorities; A.3.2 AI roles and responsibilities | GOVERN 2 (accountability structures in place) | `.agent/AGENT-ROSTER.md`, `.agent/souls/`, `subagents/install-config.json` | `python3 automation/validate_template.py` (roster/soul/mandatory-agent checks) |
| 2 | Specialization ownership map (156 packages, each with an accountable owner) | No capability operates without a responsible owner; vendored tools cannot become unaccountable actors | A.10.2 Allocating responsibilities; A.4.4 Tooling resources | GOVERN 2; GOVERN 6 (third-party software risks) | `subagents/specialization-ownership-map.json`, `subagents/GOVERNANCE_WRAPPER.md` | `validate_template.py` (full-coverage check); `validate_runtime.py` (enforces 156) |
| 3 | Sprint Zero discovery interview + spec validation (Lock 0) | Context, mission, constraints, and authority boundaries are established before any build work | A.6.2.2 AI system requirements and specification; 8.1 Operational planning and control | MAP 1 (context established and understood) | `KICKOFF.md`, `PROJECT.md`, `orchestration/system_spec.md`, `directives/director-interview-protocol.md` | `python3 automation/validate_spec.py --mode template orchestration/system-spec-template.md` |
| 4 | Mission risk profile at Gate 1 | Project-level risks and impacts are characterized before execution | 6.1.4 AI system impact assessment; A.5.2 AI system impact assessment process | MAP 5 (impacts characterized) | `docs/verification/mission-risk-profile.md`, `.governance/Phase_Gates/Gate1_BusinessUnderstanding/` | Inspect the populated profile in a generated project; gate record must cite it |
| 5 | Phase gates with Security & Compliance Officer review (CPMAI 1–6) | Work cannot advance phases without an evidence-cited human gate decision | A.6.1.3 Processes for responsible AI system design and development; 8.1 | MANAGE 1 (risks prioritized, responded to, managed) | `.governance/Phase_Gates/`, `directives/structural-integrity-protocol.md`, `.governance/security-compliance/evidence-traceability.md` | Gate approval requires an explicit approved record citing evidence (scaffold presence ≠ approval, per `CLAUDE.md`) |
| 6 | Fail-closed authority store + gatekeeper | Implementation, deployment, external writes, CDRL submission, risk acceptance, and control closure are all denied unless explicitly granted | A.6.2.5 AI system deployment; A.9.4 Intended use of the AI system; 8.1 | GOVERN 1 (policies/processes implemented effectively) | `.governance/gate_state.json` (ships all-false), `automation/gatekeeper.py` | `python3 -m pytest tests/` (authority tests); `validate_template.py` (authority-token check) |
| 7 | Dispatch task packets | Every autonomous dispatch records what was authorized, under which gate state, with explicit non-authorities | A.6.2.8 AI system recording of event logs | GOVERN 1 | `docs/verification/factory-runs/<ts>-<task>.json` | Run `./automation/factory.sh` with a shell adapter; inspect the packet |
| 8 | Post-dispatch detective stops + run results | After each autonomous run: git-audited unauthorized-write check, evidence-existence check, status-transition check; pass/violation persisted | A.6.2.6 AI system operation and monitoring; A.6.2.8 | MANAGE 4 (risk treatments documented and monitored); MEASURE 3 (mechanisms for tracking risks over time) | `docs/verification/factory-runs/<ts>-<task>-result.json`, `automation/governed_factory.py` (`post_dispatch_checks`) | `python3 -m pytest tests/` (detective-control tests) |
| 9 | Override register + fail-closed evidence rule | Exceptions are recorded events, never silent; missing evidence blocks gates unless an authorized override exists | 10.2 Nonconformity and corrective action; A.3.3 Reporting of concerns | GOVERN 4 (culture that considers and communicates risk) | `.governance/security-compliance/override-register.md`, `directives/ai-governance-framework.md` (Fail-Closed Rule) | Register must contain one row per override; empty register on Draft project is the healthy state |
| 10 | Evidence index + traceability chain | Task → evidence → verification → gate decision is walkable end to end | 7.5 Documented information (7.5.1–7.5.3) | GOVERN 1 | `docs/verification/evidence-index.md`, `.governance/Cross_Cutting/Evidence_Index/`, `.governance/security-compliance/evidence-traceability.md` | Follow any task's `Evidence Required` paths from `orchestration/tasks.md` |
| 11 | Whole-template validation + CI | The control set itself is executable and re-verified on every change; verdicts are machine-state-independent | A.6.2.4 AI system verification and validation | MEASURE 1 (appropriate methods and metrics applied); MEASURE 4 (feedback on measurement efficacy) | `automation/validate_template.py`, `automation/smoke_test_template.py`, `tests/`, `.github/workflows/validate.yml`, CI run history | `python3 automation/validate_template.py && python3 automation/smoke_test_template.py && python3 -m pytest tests/` |
| 12 | Third-party provenance and attribution | Vendored content is identified, licensed, attributed, and owner-mapped — supply chain is visible | A.10 Third-party and customer relationships | GOVERN 6; MANAGE 3 (third-party risks managed) | `THIRD_PARTY_LICENSES.md`, `subagents/SPECIALIZATION-LIBRARY.md` (boundary section) | Compare vendored file headers/upstream links against the notice |
| 13 | Claims-integrity fence | Unmapped frameworks stay labeled "Reference Needed"; fabricating compliance mappings is prohibited | 7.5.3 Control of documented information | GOVERN 4 | `directives/templates/standards-crosswalk-matrix.md`, `README.md` framework table, this file's scope statement | `validate_template.py` (ISO 27701 gap-label check) |
| 14 | Versioned change record + tamper-evident history | Every control change is attributable and dated; the governance system's own evolution is auditable | 7.5.2 Creating and updating documented information | GOVERN 1 | `CHANGELOG.md` (SemVer), git history, signed pin in the parent portfolio monorepo | `git log -- automation/ directives/ .governance/` |

## Known gaps (stated on purpose)

- **Organization-level clauses are out of repo scope:** clause 5.1 (leadership
  and commitment), 7.2 (competence), 9.2 (internal audit), and 9.3 (management
  review) require an operating organization, not a template. When the factory
  is adopted inside an AIMS (e.g., an ISO 42001-certified organization), those
  clauses attach to the adopter and this matrix supplies the operational
  control layer beneath them.
- **Pre-dispatch action inference is keyword-based** (see README "Known
  limitations"); rows 8 and 9 are the compensating detective controls.
- **NIST AI RMF GOVERN 3 (workforce diversity/inclusion) and GOVERN 5
  (engagement with external AI actors)** are organizational functions with no
  factory-level mechanism; they are intentionally unmapped rather than
  stretched.

*Maintained by: Human Director. Update this matrix in the same change that
adds, removes, or weakens any mechanism it cites.*
