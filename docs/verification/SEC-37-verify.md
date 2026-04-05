# SEC-37 Verification

## Scope

Validate the Phase 0 control-plane scaffolding introduced for the v4 source-catalog and generated-runtime pattern.

## Checks

1. Confirm the new source-catalog structure exists under `subagents/`.
2. Run `automation/install-subagents.sh` against `subagents/install-config.json`.
3. Verify the generated runtime manifest and TOMLs land in `.codex/agents/`.
4. Confirm startup docs now instruct agents to validate the runtime manifest before acting.

## Results

- `subagents/` now exists with `global/`, `project-specific/`, and `dod-regulated/` tiers plus `GOVERNANCE_WRAPPER.md` and `install-config.json`.
- `automation/install-subagents.sh` completed successfully against the default Phase 0 profile.
- `.codex/agents/runtime-manifest.json` and five runtime TOMLs were generated:
  - `scrum-master.toml`
  - `program-analyst.toml`
  - `documentation-se.toml`
  - `pipeline-devops.toml`
  - `security-compliance-officer.toml`
- Determinism spot-check passed on a second installer run.
- Runtime manifest SHA-256: `a5b38912c661ee0b35ee733816c7782293e19c0e43543edebe09e98d1a464b4d`
- `CODEX.md` and `CLAUDE.md` now require agents to validate `.codex/agents/runtime-manifest.json` when present before acting.

## Residual Notes

- The repo already contained unrelated local modifications before this task started; they were preserved.
- Google Drive journal folder resolution failed from the current `gws` session, so this heartbeat’s trace artifact is local to the repo instead of appended to Drive.
