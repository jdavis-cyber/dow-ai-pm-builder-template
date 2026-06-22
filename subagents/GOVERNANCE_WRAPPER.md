# Governance Wrapper for Runtime and Specialization Packages

All TOML packages under `subagents/` must preserve the template's discovery-first and factory-governance controls.

## Package Classes

- **Accountable agents**: the permanent 15-agent scrum team listed in `.agent/AGENT-ROSTER.md` and installed by `subagents/install-config.json`.
- **Specialization packages**: the 136 VoltAgent capability packages mapped in `subagents/specialization-ownership-map.json`.
- **Regulated overlays**: optional product/engagement overlays activated only when project classification requires them.

## Required Metadata

Each accountable package must declare `name`, `version`, `tier`, `source_soul`, and `owner_role`.

Each specialization map entry must declare accountable owner or `reference-only`, activation condition, reason for selection, source TOML path, and evidence obligations.

## Non-Override Rules

1. Runtime packages do not replace the governing SOUL file; they operationalize it.
2. Specializations cannot override SOUL duties, Double-Lock phase gates, fail-closed controls, or evidence obligations.
3. Security & Compliance Officer is mandatory for the base factory; product-specific overlays do not control whether Agent 15 exists.
4. Missing accountable runtime packages are install failures. Agents must stop and escalate instead of improvising.
