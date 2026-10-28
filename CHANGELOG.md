# Changelog

All notable changes to the DoW AI PM Builder Template are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning
follows SemVer aligned to the template's major revisions.

## [Unreleased]

### Fixed
- Codex starts generated projects in a read-only sandbox until Sprint Zero sign-off
  or a signed Human Director implementation override (AI-1176 / DEF-017).
  Before authority, `approval_policy = "on-request"` lets the human approve each
  planning write while `sandbox_mode = "read-only"` blocks unapproved writes.
  Guidance forbids approving source writes before sign-off; the skip path requires
  a signed override row. The native probe retains source-write refusal checks.
  `gatekeeper.py sign` signs the gate state and override register digest with the
  existing external operator key. Unsigned, edited-after-signing, expired, or
  malformed rows grant nothing; a failed gate-state signature also denies overrides.
  This applies to both action checks and Codex config (ADR-002).
  Operators refresh permissions with
  `python3 automation/codex_config.py codex-config` and start a new session;
  `gatekeeper.py sign` also refreshes existing generated configurations.

### Model chosen per session
- Removed the hardcoded `model` (`gpt-5.4`, `gpt-5.3-codex-spark`) and
  `model_reasoning_effort` pins from the 136 vendored VoltAgent packages; the
  operator picks model and effort in the adapter command (see INSTALL.md).
  Validation fails if any agent package pins either again.

### Seeded board reaches Gate 1 (JER-26)
- The task board (template and the template's own `orchestration/tasks.md`)
  now seeds the full Sprint Zero → Gate 1 chain: the eight playbook
  interviews, Lock 0 spec validation, classification capture, Mission Risk
  Profile and Governance Scope Statement, the Security & Compliance Officer's
  Gate 1 review, the Gate 1 readiness package and the Director's Gate 1
  decision, where the dispatcher stops for the human.

### Security & Compliance Officer is mandatory everywhere (JER-24)
- `security-compliance-officer.toml` moved from `subagents/dod-regulated/` to
  `subagents/global/`; the activation matrix and classification rules now say
  the SCO participates on every project and only the regulated overlays are
  conditional. `validate_template.py` fails if the SCO is made conditional,
  moved back to the overlay tier, or dropped from the roster.

### Plan-before-build (JER-25)
- Optional task fields `Human Gate: yes|no` and `Plan: <path>`, plus statuses
  `Planned` and `Plan Approved`. A Human Gate task is first dispatched only to
  write its plan (no authority; the write audit flags anything else), then
  waits in `Planned`.
- The Director approves with `gatekeeper.py approve-plan TASK-ID <plan>`, which
  records an operator-signed approval of that exact plan; `Plan Approved` tasks
  dispatch only while that approval verifies.
- `validate_tasks.py` requires a Plan for Human Gate tasks and Human Gate for
  Phase IV–VI tasks whose Gate Impact isn't `none`.
- New `directives/templates/implementation-plan.md`, Lock 1.5 in the
  structural-integrity protocol, a Plan Approval Request touchpoint, and a
  Scrum Master rule to route plan approvals to the Director.

### Assisted mode and generated projects (JER-46)
- Assisted mode now gets the same detective checks: the dispatcher records the
  tree and evidence state when it hands a task to a human, and on the next run
  after the task leaves Ready it runs the write audit, evidence and status
  checks and records a result (pass or violation).
- Generated projects now receive `SECURITY.md`, so the validation commands
  they are told to run (`validate_template.py`, `smoke_test_template.py`) pass there.
- Tag a new template version after these fixes merge so projects instantiated
  before them can be identified from `TEMPLATE_PROVENANCE.md`.

### Instruction-file integrity (JER-41)
- Each vendored specialization package has a SHA-256 in
  `subagents/specialization-ownership-map.json`; `validate_template.py` and
  `install_subagents.py` fail on a mismatch. After reviewing an intended
  change, record it with `python3 automation/vendor_digests.py update`.
- The runtime manifest records a digest for every materialized agent TOML;
  `validate_runtime.py` and the dispatcher refuse a bundle edited after install.

### Structured authority and dispatch boundary (JER-42, JER-40)
- Tasks declare `**Requires Authority**` (`none` or a list such as
  `implementation, deploy`); the validator rejects bad values and the
  dispatcher refuses a task without a valid one. Keyword matches can only add
  checks, and negations or "planning only" no longer suppress a check or stop.
- The adapter prompt fences task-board text as untrusted data and no longer
  carries the authority state.
- The adapter gets a minimal environment; credentials pass only when named in
  `FACTORY_ADAPTER_ENV_PASSTHROUGH`.
- `factory.dispatch` sets the content classification and the adapter's
  approved ceiling; DoD-regulated projects and CUI-marked task text are CUI,
  and dispatch above the ceiling is refused before anything is sent.
- `--loop` requires a committed (reviewed) task board.

### Evidence integrity and bounded execution (JER-43, JER-38)
- Evidence must be non-empty, a task must declare at least one evidence path,
  and a status change with no changed evidence is a violation.
- Run results record evidence SHA-256s, the adapter command, model id and
  provider version (`FACTORY_MODEL_ID`, `FACTORY_PROVIDER_VERSION`), and the
  tail of the adapter's stdout/stderr. Results are hash-chained
  (`docs/verification/factory-runs/chain/head.json`); a broken chain stops dispatch.
- Task packets are recorded by default.
- `factory.limits` bounds the loop (`max_iterations`, `max_wall_seconds`), each
  adapter run (`adapter_timeout_seconds`) and optional spend
  (`max_tokens`, `max_cost_usd`, reported by the adapter via `FACTORY_USAGE_FILE`).
- `stop_on` is enforced: a config that drops a stop or names an unknown one is
  refused, and `dirty_unexpected_state` stops dispatch when uncommitted changes
  sit outside the agent's write scope.

### Authority store and write audit (JER-39, JER-37)
- `.governance/` is no longer agent-writable: the gatekeeper denies writes there
  whatever the authorization state, and the post-dispatch audit flags any change.
- A gate state that grants authority must carry an operator HMAC signature
  (`gatekeeper.py sign`, key kept outside the project). Unsigned or tampered
  states fail `verify-consistency`, so dispatch is refused.
- The write audit fails closed when git is unusable, sees both sides of a
  rename (`git status -z`), flags every non-planning path the gatekeeper would
  deny, and attributes changes to files that were already dirty by content digest.

### Requirement remediation — 2026-10-01
- SR-04: locked specs reject bounded unresolved `Gap` markers while preserving ordinary gap prose.
- SR-08: every post-dispatch violation halt points to the override register and explicitly grants no authority.
- SR-16: failed adapters retain a run result and all detective checks. A nonzero adapter exit keeps its code and primary failure outcome; simultaneous detective findings remain in the record. Successful adapters retain first-violation outcome and exit 3.
- Added requirement acceptance and regression cases using isolated deterministic fixtures. Human discovery, real-project evidence, multiplatform and live-runtime qualification remain outside these execution results.
### Framework mapping documents removed
- Removed `docs/governance-frameworks/` (control matrix, statement of
  applicability, factory risk register, objectives, model-supplier criteria,
  example AI policy, framework status and the maintenance-scope note). The
  repository holds no framework mappings or self-assessments; generated
  projects no longer receive copies. README, the governance-scope directive,
  the documentation map, the generator and the smoke test no longer point at
  them. Earlier changelog entries are kept as history.

### Repository maintenance cleanup
- Removed mandatory presence/exact-prose checks for six duplicate assurance
  references and the crosswalk's gap-label wording from `validate_template.py`.
- Marked those references optional and removed recurring repository review
  obligations. Existing links and historical assessment material are retained.
- Retained `whole-template`, runtime/roster/spec/task validation, project
  generation, security checks, gatekeeper behavior and metrics.
- Added regressions proving optional paperwork can be omitted while missing
  authority controls still fail validation.

### Earlier assurance additions (historical scope)

Factory assurance layer (AI-547…AI-551): the reverse sweep to the control
matrix, plus the assurance artifacts it depends on. Each carries a
verified-SHA stamp from the 2026-07-10 assessment; the maintenance cleanup
above removes that recurring rule.

### Added
- `docs/governance-frameworks/factory-soa.md` — Statement of Applicability:
  explicit disposition for every ISO/IEC 42001 Annex A control (A.2–A.10) and
  every NIST AI RMF category, incl. MAP 2 factory categorization; grounded
  citations; consolidated known-gaps taxonomy (adopter-attached /
  operationally-gated / intentionally unmapped).
- `docs/governance-frameworks/factory-risk-register.md` — 17 factory-level
  risks (FR-01…FR-17, incl. the adversarial-review seed set: adapter
  compromise, prompt injection, evidence fabrication, model drift) with
  treatments mapped to operating mechanisms.
- `docs/governance-frameworks/factory-objectives.md` — measurable factory
  objectives (FO-1…FO-5: metric, target, threshold, method, frequency, owner)
  and `automation/factory_metrics.py` aggregating run-result records, with
  regression tests (`tests/test_factory_metrics.py`).
- `docs/governance-frameworks/model-supplier-criteria.md` — runtime-provider
  selection/review criteria with review triggers and an organization-record
  bridge.
- `docs/governance-frameworks/factory-ai-policy.md` — the factory's own AI
  policy with explicit review cadence (version bump + annual).
- `SECURITY.md` — incident-communication path for template users (advisory +
  CHANGELOG + in-repo correction).
- `validate_template.py` guards for all five assurance docs (existence +
  honesty-language needles) and the metrics script.

### Changed
- Automation script count is 14 (`factory_metrics.py` added); README metric
  updated from the 13 stated at v4.1.0.
- `structural-integrity-protocol.md` §4 corrected: interview order now defers
  to `orchestration/sprint-zero-playbook.md` (the operative sequence, BA first)
  instead of restating a stale UI/UX-first order (DEF-015).

## [4.1.0] — 2026-07-10

Public-readiness hardening pass (adversarial pre-publication review).

### Added
- `docs/governance-frameworks/factory-control-matrix.md` — 14 factory mechanisms clause-mapped to ISO/IEC 42001 and NIST AI RMF with evidence pointers, per-row verification commands, and an explicit known-gaps section; guarded by `validate_template.py`.
- Factory self-evidence: every autonomous dispatch persists a run-result record (checks run, pass/violation) alongside the task packet in `docs/verification/factory-runs/`.
- Post-dispatch detective stops in `automation/governed_factory.py` (shell adapter): git-audited unauthorized protected-source writes, missing-evidence halt, and open-task redispatch guard — with regression tests in `tests/test_governance_gates.py`.
- `.governance/gate_state.json` (fail-closed authority store) and `.governance/security-compliance/override-register.md` now ship in the template and are scaffolded by `automation/init_project.py`.
- `THIRD_PARTY_LICENSES.md` — VoltAgent attribution (both upstream collections, MIT) for the 136 vendored packages and 20 derived execution-depth wrappers.
- `SECURITY.md`, `CONTRIBUTING.md`, and CI (`.github/workflows/validate.yml`) running whole-template validation, the smoke test, and the governance test suite.
- Canonical Double-Lock definition in `directives/structural-integrity-protocol.md` §0.

### Changed
- The 20 execution-depth wrappers at `subagents/global/*.toml` are now entries in `subagents/specialization-ownership-map.json` (156 total); `validate_runtime.py` enforces 156.
- Corrected public metrics: 156-entry ownership map (was misstated as 272), 7 directives + 29 templates + 13 automation scripts (was "11 directives + 10 scripts").
- Task boards use "CPMAI Phase 1 — Business Understanding" naming, matching gate directories; evidence-traceability remediation flags cleared.
- Soul quality-gate checklists start unchecked; Director Interview Protocol no longer names a specific person as Human Director.
- `validate_template.py`: stale-string scan skips generated/ignored directories (machine-state-independent verdict) and enforces CLAUDE/CODEX/GEMINI provider-file sync.

## [4.0.0] — 2026-06-11

First tagged release of the v4.0 (DoW Regulated Edition) line, hardened for
fresh-machine installation and external demonstration.

### Added
- `INSTALL.md`: fresh-machine setup, agent activation, verification
  checklist, troubleshooting — every step executed and verified
- `CLAUDE.local.md` pattern: gitignored, machine-local operator context

### Changed
- `CLAUDE.md` is machine-agnostic: operator-specific binary paths, accounts,
  and knowledge-corpus IDs extracted to the gitignored local file

### v4.0 line (2026-03 → 2026-05, pre-tag)
- 15-agent DoW regulated roster with TOML subagent catalog (136
  specializations) and `install-subagents.sh` runtime materialization
- Double-Lock phase-gate protocol (operational readiness + governance
  clearance), fail-closed zero-TBD spec validation
- ISO 42001 evidence mapping, DoW requirements set, NotebookLM corpus
  integration
