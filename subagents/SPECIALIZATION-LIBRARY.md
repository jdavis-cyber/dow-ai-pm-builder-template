# Specialization Library — 156 Capability Packages

The template includes **156 specialization packages**: 136 vendored VoltAgent packages under `subagents/global/voltagent/` and 20 governed execution-depth wrappers at `subagents/global/*.toml`. These TOML files are tools/capabilities used by the 15 accountable agents. They are not autonomous accountable peer agents. They are adapted from the MIT-licensed [VoltAgent awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) collection — attribution and upstream license text in `THIRD_PARTY_LICENSES.md` at the repo root.

**Boundary:** the root level of `subagents/global/` holds two kinds of packages. The **14 accountable-agent identity packages** (names matching `.agent/souls/`) are this repository's own work, generated from the souls; the 15th accountable agent, `security-compliance-officer`, lives in `subagents/dod-regulated/`. The **20 execution-depth wrappers** (headers citing an upstream `Source:`) are VoltAgent-derived with governance metadata added — see `THIRD_PARTY_LICENSES.md`. Where a root package and a vendored package share a name (e.g. `backend-developer`), the root package is the accountable owner's identity; the vendored package is a selectable capability mapped to that owner.

Machine-readable ownership lives in `subagents/specialization-ownership-map.json` and must cover every VoltAgent TOML.

## Use Rules

1. An accountable owner must activate the specialization for a task-specific reason.
2. The owner remains accountable for outputs, verification, handoff, and evidence indexing.
3. A specialization cannot weaken SOUL duties, phase gates, fail-closed controls, or evidence obligations.
4. If no accountable owner is appropriate, the package must be explicitly marked `reference-only` with rationale.

## Inventory

- Total VoltAgent TOMLs mapped: 136
- Ownership map: `subagents/specialization-ownership-map.json`
