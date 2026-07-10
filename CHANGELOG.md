# Changelog

All notable changes to the DoW AI PM Builder Template are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning
follows SemVer aligned to the template's major revisions.

## [Unreleased]

Factory assurance layer (AI-547…AI-551): the reverse sweep to the control
matrix, plus the assurance artifacts it depends on. Each carries a
verified-SHA stamp per the standing rule from the 2026-07-10 cohesion audit.

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
