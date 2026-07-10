# ADR-001: Template Source Catalog And Generated Runtime Agents

## Status

Proposed

## Context

The live DoW PM Builder template is still organized around `.agent/souls/` and does not yet contain the v4 TOML runtime surfaces assumed by the 2026-03-24 master plan. The target design must reconcile:

- template-owned SOUL files,
- a future TOML library,
- project-local runtime activation,
- regulated overlays for DoD and similar environments,
- and the operator's canonical workspace root (machine-local; not part of the template).

## Decision

Adopt a split packaging model:

- `.agent/souls/` holds durable role identity and governance constraints.
- `subagents/` holds versioned TOML source packages in `global`, `project-specific`, and `dod-regulated` tiers.
- `.codex/agents/` is generated from the selected TOML set during project initialization and is the only runtime location agents depend on.

The Security & Compliance Officer is introduced as a new SOUL and paired with regulated-tier TOMLs instead of embedding compliance logic into unrelated roles.

## Consequences

Positive:

- deterministic project initialization
- cleaner regulated-project isolation
- easier audits because source and generated assets are distinct
- safer reinstallation and upgrade path

Negative:

- requires installer tooling and config validation before use
- adds one more layer for operators to understand
- requires startup protocol changes so agents fail when expected TOMLs are absent

## Follow-On Work

- Create `subagents/install-config.json`.
- Create `automation/install-subagents.sh`.
- Add `security-compliance-officer.md`.
- Update `CODEX.md` and `CLAUDE.md` startup checks.
