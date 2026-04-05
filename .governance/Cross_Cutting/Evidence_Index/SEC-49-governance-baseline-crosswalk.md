# SEC-49 Governance Baseline Crosswalk And Phase-Gate Evidence Gaps

## Document Metadata

| Field | Value |
| --- | --- |
| Document ID | SEC-49-GBX-2026-03-29 |
| Status | Draft |
| Author | Program Analyst |
| Source Issue | [SEC-49](/SEC/issues/SEC-49) |
| Repository Scope | `/Volumes/WORKSPACE/DoW PM Builder Template` |
| Governing References | `directives/ai-governance-framework.md`, `docs/architecture/SEC-36-gate1-control-artifact-spec.md` |

## Purpose

Establish the minimum repo-grounded control crosswalk and evidence baseline needed to support the AI governance framework rewrite and future compliant AI system packaging. This artifact records what evidence already exists, where control coverage is only templated, where duplicate governance surfaces exist, and which gaps currently block enforceable phase-gate execution.

## Evidence Basis

This baseline uses only repository-grounded artifacts present on 2026-03-29:

- `orchestration/system_spec.md`
- `docs/product/project-classification-inputs.md`
- `docs/verification/sec-35-verify.md`
- `docs/architecture/SEC-36-gate1-control-artifact-spec.md`
- `directives/ai-governance-framework.md`
- `directives/templates/TEMPLATE-INDEX.md`
- `directives/templates/phase-gate-review.md`
- `directives/templates/standards-crosswalk-matrix.md`
- `directives/templates/evidence-index.md`
- `.governance/**` scaffold paths

## 1. Baseline Evidence Inventory

| Artifact | Current State | Evidence Type | Primary Control Anchors | Notes |
| --- | --- | --- | --- | --- |
| `orchestration/system_spec.md` | Present, Section A drafted, downstream sections intentionally locked | Discovery evidence | CPMAI Phase I, ISO 42001 Clauses 4.3/5.1/6.1, NIST AI RMF GOVERN, CSRMC mission and control-scope entry conditions | Valid discovery input, but not a signed gate artifact |
| `docs/product/project-classification-inputs.md` | Present | Discovery evidence | CPMAI Phase I, NIST AI RMF GOVERN-1/GOVERN-2, ISO 42001 scope and role definition, CSRMC overlay decision logic | Canonical classification rules for regulated overlay activation |
| `docs/verification/sec-35-verify.md` | Present | Verification evidence | ISO 42001 Clause 7.5, NIST AI RMF GOVERN traceability, CPMAI Gate 1 readiness support | Confirms Section A and classification note exist, but does not close Gate 1 |
| `docs/architecture/SEC-36-gate1-control-artifact-spec.md` | Present, approved specification | Governance design evidence | CPMAI Gate 1, ISO 42001 Clause 9.3 and 7.5, NIST AI RMF GOVERN, CSRMC control-traceability | Only approved repo-grounded Gate 1 artifact contract |
| `directives/ai-governance-framework.md` | Present | Governing directive | CPMAI lifecycle baseline, ISO 42001, NIST AI RMF, CSRMC, NIST overlays, OMB M-24-10 | Active reference, not project-specific execution evidence |
| `directives/templates/TEMPLATE-INDEX.md` | Present | Template inventory | CPMAI artifact catalog, ISO 42001/NIST AI RMF/CSRMC artifact intent | Defines expected artifact set only |
| `directives/templates/standards-crosswalk-matrix.md` | Present, uninstantiated | Template | ISO 42001 Clause 6.1.3, NIST AI RMF cross-cutting, CSRMC/CPMAI mapping intent | No project-specific control mapping populated |
| `directives/templates/phase-gate-review.md` | Present, defective for framework alignment | Template | CPMAI phase-gate package, ISO 42001 Clause 9.3 | Gate 1 needs corrections; Gates 2-6 are phase-misaligned |
| `directives/templates/evidence-index.md` | Present, uninstantiated | Template | ISO 42001 Clause 7.5, CSRMC AEP, NIST SP 800-53 AU-1 | Phase naming inside template is not framework-accurate |
| `.governance/Phase_Gates/**` | Scaffold only (`.gitkeep`) | Empty control repository | Intended CPMAI hard-gate record location | No enforceable gate package exists |
| `.governance/Cross_Cutting/**` | Scaffold only (`.gitkeep`) | Empty control repository | Intended SoA, Risk Register, Evidence Index, CSRMC baseline location | No cross-cutting governance baseline exists |

## 2. Control Anchor Crosswalk

| Control Anchor | Existing Repo-Grounded Coverage | Duplicate Or Overlapping Surfaces | Missing Evidence Needed For Enforceable Use |
| --- | --- | --- | --- |
| PMI-CPMAI lifecycle and hard-gate sequencing | `directives/ai-governance-framework.md`, `orchestration/system_spec.md`, `docs/architecture/SEC-36-gate1-control-artifact-spec.md` | `directives/templates/phase-gate-review.md`, `PROJECT.md` governance table | `gate-status.md`, populated Gate 1 review package, approved sign-off record, later-gate template remediation |
| ISO/IEC 42001 AIMS scope, documentation, and control selection | `directives/ai-governance-framework.md`, `docs/product/project-classification-inputs.md`, `docs/verification/sec-35-verify.md`, `SEC-36` | `standards-crosswalk-matrix.md`, `statement-of-applicability.md` template, `evidence-index.md` template | Populated SoA, evidence index, risk register, documentation control record, approved applicability decisions |
| NIST AI RMF GOVERN-led lifecycle governance | `ai-governance-framework.md`, `system_spec.md`, `project-classification-inputs.md`, `SEC-36` | `standards-crosswalk-matrix.md`, `mission-risk-profile.md` and governance review templates | Populated mission risk profile, governance cadence records, formal gate decision package, residual-risk acceptance trace |
| DoD CSRMC modernization overlay and compliant AI packaging support | `ai-governance-framework.md`, `project-classification-inputs.md`, `SEC-36` | `TEMPLATE-INDEX.md`, `standards-crosswalk-matrix.md` | Critical-controls mapping, security-compliance traceability tree, regulated approval records, AEP and CCV baseline paths |

## 3. Duplicated Or Conflicting Governance Surfaces

| ID | Surface | Duplicate Or Conflict | Operational Impact |
| --- | --- | --- | --- |
| D1 | `orchestration/system_spec.md` and `docs/product/project-classification-inputs.md` | Both encode classification rules and authority boundaries | Acceptable duplication for discovery support, but one cross-reference note should identify the canonical rule source to avoid drift |
| D2 | `directives/ai-governance-framework.md`, `TEMPLATE-INDEX.md`, and `standards-crosswalk-matrix.md` | All describe artifact intent and standards relationships at different abstraction levels | Easy to mistake template intent for implemented evidence |
| D3 | `directives/templates/phase-gate-review.md` and `docs/architecture/SEC-36-gate1-control-artifact-spec.md` | Template deliverables and metadata do not match the approved Gate 1 artifact contract | Gate package authors can generate noncompliant records if they follow the template instead of `SEC-36` |
| D4 | `directives/templates/evidence-index.md` and `ai-governance-framework.md` | Evidence index template uses phase labels that diverge from the active CPMAI phase names in the directive | Audit trail can drift from the governing lifecycle taxonomy |
| D5 | `PROJECT.md` and `.governance/**` | `PROJECT.md` advertises governance artifact locations that are not populated | Creates a false impression of gate readiness |

## 4. Phase-Gate And Control Gaps

| Gap ID | Gap | Severity | Evidence Basis | Blocking Effect |
| --- | --- | --- | --- | --- |
| G1 | No populated Gate 1 control artifacts exist under `.governance/Phase_Gates/Gate1_BusinessUnderstanding/` | High | Repo contains only `.gitkeep` in every phase-gate directory | Gate 1 cannot run as a hard gate |
| G2 | No cross-cutting SoA, Risk Register, or Evidence Index exists under `.governance/Cross_Cutting/` | High | Repo contains only `.gitkeep` in each cross-cutting directory | ISO 42001 control selection, NIST traceability, and CSRMC evidence bundling are not enforceable |
| G3 | No `.governance/security-compliance/` tree exists | High | `SEC-36` requires this tree; repo does not contain it | Regulated review records and approval evidence have no canonical home |
| G4 | `directives/templates/phase-gate-review.md` is not framework-accurate for Gates 2-6 and lacks Gate 1 required metadata and sign-off controls | High | Direct comparison of template to `ai-governance-framework.md` and `SEC-36` | Later gate packages will be structurally noncompliant if authored from the current template |
| G5 | `directives/templates/standards-crosswalk-matrix.md` remains a blank template | Medium | No project-specific mapping is populated | Control coverage is described in principle but not instantiated for this repo |
| G6 | `directives/templates/evidence-index.md` still uses outdated phase naming and placeholder content | Medium | Template content does not match the active six-phase taxonomy | Evidence indexing can drift from the governing lifecycle model |
| G7 | `orchestration/system_spec.md` is explicitly still a draft and there is no approval record in `.governance/` | Medium | System spec header and absence of sign-off artifacts | Governance packaging cannot claim approved discovery baseline yet |
| G8 | Standing operator instructions contain stale Drive folder names and IDs | Low | Verified during this heartbeat; live folders are `Inbox`, `Outbox`, `Daily Journals` with different IDs | Review artifacts can be routed incorrectly outside the repo workflow |

## 5. Minimum Sequencing Recommendation

1. Materialize Gate 1 control records first: `gate-status.md`, `phase-gate-review.md`, `mission-risk-profile.md`, `governance-scope-statement.md`.
2. Materialize the cross-cutting baseline next: `statement-of-applicability.md`, `risk-register.md`, `evidence-index.md`.
3. Create `.governance/security-compliance/` and its traceability files exactly as required by `SEC-36`.
4. Patch `directives/templates/phase-gate-review.md` and `directives/templates/evidence-index.md` so template behavior matches the active framework.
5. Instantiate the standards crosswalk from template into a project-specific control map only after the canonical artifact paths above exist.

## 6. Residual Risk

- Until Gate 1 artifacts are materialized, the repository can support discovery and control design review, but it cannot support audit-ready phase-gate approval.
- Until template defects are corrected, downstream specialists can unintentionally produce governance records that look complete but fail framework alignment.
- Until the cross-cutting evidence baseline exists, any claim of ISO 42001, NIST AI RMF, or CSRMC readiness is partial and design-level only.
