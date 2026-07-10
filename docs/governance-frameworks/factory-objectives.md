# Factory Objectives — Measurable Targets for the Factory's Own Operation

**Scope and honesty statement (read first).** These are objectives for
operating the factory *itself* — not product KPIs for anything the factory
builds, and not a certification claim. This is a **repo-level
self-assessment** artifact: each objective carries a metric, target, action
threshold, measurement method, frequency, and owner, so that "is the factory
operating as designed?" is answerable from evidence rather than assertion.
Organization-level objective governance (ISO/IEC 42001 clause 6.2 approval,
management review of results) attaches to the adopting organization.

Each objective defines: **Metric** · **Target** · **Threshold** (trigger for
action) · **Measurement method** · **Frequency** · **Owner**.

## FO-1 — Verified template integrity on every change

- **Metric:** CI verdict of the validation gauntlet (whole-template
  validation + smoke test + governance test suite) per push.
- **Target:** 100% of pushes to `main` green.
- **Threshold:** any red run on `main` → fix or revert before further factory
  work; recurring same-cause failures → corrective change to the validator or
  the mechanism, recorded in `CHANGELOG.md`.
- **Measurement method:** `.github/workflows/validate.yml` run history;
  locally `python3 automation/validate_template.py &&
  python3 automation/smoke_test_template.py && python3 -m pytest tests/`.
- **Frequency:** every push; reviewed at every version bump.
- **Owner:** Human Director.

## FO-2 — Complete run-result evidence for autonomous dispatches

- **Metric:** % of autonomous dispatches with a persisted run-result record
  (task packet + `<timestamp>-<task>-result.json`).
- **Target:** 100%.
- **Threshold:** any dispatch without a result record → halt autonomous
  operation, investigate the dispatcher, log the gap in the override register.
- **Measurement method:** `python3 automation/factory_metrics.py` aggregates
  `docs/verification/factory-runs/*-result.json` and reports run counts,
  violation counts, and pass rate.
- **Frequency:** per run; aggregate reviewed at every version bump.
- **Owner:** Human Director.

## FO-3 — Zero unresolved governance violations

- **Metric:** count of run-result records whose `outcome` is a violation with
  no matching resolution (corrective change or authorized override-register row).
- **Target:** 0 unresolved.
- **Threshold:** ≥1 unresolved violation → autonomous dispatch pauses until
  the violation is dispositioned (fix, or recorded override with authority).
- **Measurement method:** `automation/factory_metrics.py` violation report
  reconciled against `.governance/security-compliance/override-register.md`.
- **Frequency:** per run; aggregate at version bump.
- **Owner:** Human Director.

## FO-4 — Zero unauthorized protected-source writes

- **Metric:** unauthorized-write findings from the post-dispatch git audit.
- **Target:** 0 per version cycle.
- **Threshold:** any finding → treat as a governance incident: revert the
  write, record the event, and correct the inference or the adapter before
  the next autonomous dispatch.
- **Measurement method:** detective-stop results inside run-result records
  (`automation/governed_factory.py`, `post_dispatch_checks`); regression
  coverage in `tests/test_governance_gates.py`.
- **Frequency:** per run.
- **Owner:** Human Director.

## FO-5 — Documentation verified against the factory it describes

- **Metric:** % of factory-describing governance documents carrying a
  verified-SHA stamp no older than the last version bump.
- **Target:** 100% at every version bump.
- **Threshold:** any stale document at a version bump → re-verification pass
  before the release notes are finalized (standing rule from the 2026-07-10
  cohesion audit; see `factory-risk-register.md` FR-11).
- **Measurement method:** inspect the verification stamp line in each
  `docs/governance-frameworks/*.md` artifact against `CHANGELOG.md`.
- **Frequency:** every version bump.
- **Owner:** Human Director.

## Known gaps (stated on purpose)

- The pristine template ships **no run-result records** — FO-2/FO-3/FO-4
  aggregate to "no runs recorded yet" until a project actually dispatches
  work. That empty state is honest, not a passing grade.
- Objective results are reviewed by the Human Director; there is no
  independent management-review body at template scope (attaches to the
  adopter, clause 9.3).

*Maintained by: Human Director. Verified against commit `8991e57`
(2026-07-10); re-verify at every version bump.*
