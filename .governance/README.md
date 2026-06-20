# Governance Package README

> Template status: scaffold. Populate this README during project instantiation or Gate 1 reconstruction.

## Artifact Status

| Field | Value |
|---|---|
| Status | Draft |
| Approval State | Not Approved |
| Evidence Type | Template Scaffold |
| Owner | Program Analyst / Security & Compliance Officer |
| Last Updated | [YYYY-MM-DD] |

## Purpose

`.governance/` contains the formal governance and compliance package for the project. It is part of the same authoritative project repository as the implementation source, but source and governance remain separated by directory.

## Contents

| Path | Purpose | Notes |
|---|---|---|
| `.governance/gate_state.json` | Machine-readable phase/gate state | Protected. Do not edit manually. |
| `.governance/Phase_Gates/` | Human-readable gate packages | Approval requires the project approval mechanism. |
| `.governance/Cross_Cutting/` | Risk, SoA, evidence index, standards, corrective action | Draft until reviewed/approved. |
| `.governance/security-compliance/` | Security/compliance review support | Use for reviews, control mappings, deviations, approvals. |

## Approval Integrity Rule

Governance artifacts can be drafted by agents, but approval belongs to the human PM/PO/Director or the approved out-of-band mechanism. Do not treat copied template files, scaffolded text, or historical artifacts as approved project evidence.

## Required Project-Specific Updates

- [ ] Replace template placeholders with project-specific content.
- [ ] Confirm active gate and phase.
- [ ] Link to `docs/handoff/documentation-map.md`.
- [ ] Link to `docs/verification/` evidence records.
- [ ] Link to `docs/decisions/` decision records.
- [ ] Record known gaps and residual risks.
