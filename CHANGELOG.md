# Changelog

All notable changes to the DoW AI PM Builder Template are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/); versioning
follows SemVer aligned to the template's major revisions.

## [4.0.0] — 2026-06-11

First tagged release of the v4.0 (DoW Regulated Edition) line, hardened for
fresh-machine installation and external demonstration.

### Added
- `INSTALL.md`: fresh-machine setup, agent activation, verification
  checklist, troubleshooting — every step executed and verified
- `DEMO.md`: scripted auditor (ISO/IEC 42001) and executive walkthroughs
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
