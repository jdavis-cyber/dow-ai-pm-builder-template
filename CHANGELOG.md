# Changelog

All notable changes to the DoW AI PM Builder Template are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning
follows SemVer aligned to the template's major revisions.

## [4.1.0] — 2026-07-10

Public-readiness hardening pass (adversarial pre-publication review).

### Added
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
