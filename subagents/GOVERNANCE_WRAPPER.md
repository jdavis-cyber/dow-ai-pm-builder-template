# Governance Wrapper For Runtime Packages

All TOML packages under `subagents/` must preserve the template's discovery-first and regulated-environment controls.

## Required Metadata

Each package must declare:

- `name`
- `version`
- `tier`
- `source_soul`
- `owner_role`

## Required Governance Rules

1. Runtime packages do not replace the governing SOUL file; they operationalize it.
2. Packages must not weaken the Double-Lock or phase-gate requirements.
3. Regulated overlays must stay project-local and activate only through explicit profile traits.
4. Missing runtime packages are install failures. Agents must stop and escalate instead of improvising.
5. Security and compliance review packages remain reviewers and gate participants, not default implementation workers.
