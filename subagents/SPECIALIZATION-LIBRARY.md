# Specialization Library — 136 VoltAgent Capability Packages

The template includes **136 VoltAgent specialization packages** under `subagents/global/voltagent/`. These TOML files are tools/capabilities used by the 15 accountable agents. They are not autonomous accountable peer agents.

Machine-readable ownership lives in `subagents/specialization-ownership-map.json` and must cover every VoltAgent TOML.

## Use Rules

1. An accountable owner must activate the specialization for a task-specific reason.
2. The owner remains accountable for outputs, verification, handoff, and evidence indexing.
3. A specialization cannot weaken SOUL duties, phase gates, fail-closed controls, or evidence obligations.
4. If no accountable owner is appropriate, the package must be explicitly marked `reference-only` with rationale.

## Inventory

- Total VoltAgent TOMLs mapped: 136
- Ownership map: `subagents/specialization-ownership-map.json`
