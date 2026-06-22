# Project Continuation Guide

> Template status: scaffold. Populate this file before handoff, restart, or external review. Do not use it to imply gate approval.

## Artifact Status

| Field | Value |
|---|---|
| Status | Draft |
| Approval State | Not Approved |
| Evidence Type | Template Scaffold |
| Owner | Scrum Master / Program Analyst |
| Last Updated | [YYYY-MM-DD] |

## Purpose

This guide lets a future human or agent continue the project from a fresh clone without reconstructing context from chat history or a separate builder repo.

## Startup Protocol

1. Read `PROJECT.md`.
2. Read `docs/handoff/documentation-map.md`.
3. Read `orchestration/system_spec.md`.
4. Read the active coordination file for the runtime: `CLAUDE.md`, `CODEX.md`, or `GEMINI.md`.
5. Read `directives/structural-integrity-protocol.md` and `directives/ai-governance-framework.md`.
6. Check `.governance/Phase_Gates/` for the active gate and phase.
7. Check `orchestration/tasks.md`.
8. Inspect `git status --short --branch` before changing files.
9. Do not write to implementation paths until the applicable phase gate is approved by the PM/PO.

## Current Project Snapshot

| Field | Value |
|---|---|
| Project Name | [Project Name] |
| Project ID | [Project ID] |
| Primary Repo | [URL/path] |
| Template Source | [Template repo URL] |
| Template Commit | [SHA] |
| Current Branch | [branch] |
| Current Phase | [I-VI] |
| Active Gate | [Gate Name] |
| Gate Status | [Not Approved / Ready for Verification / Approved / Conditional / No-Go] |

## Implementation Surfaces

List the source/runtime paths actually used by this project.

| Path | Purpose | Gate Protected? | Notes |
|---|---|---:|---|
| `src/` | [UI/API/library source] | Yes | [notes] |
| `services/` | [microservices] | Yes | [notes] |
| `packages/` | [workspace packages] | Yes | [notes] |
| `database/` | [schema/migrations] | Yes | [notes] |
| `infrastructure/` | [deployment/IaC] | Yes | [notes] |
| `execution/` | [optional legacy implementation] | Yes | [notes] |

## Governance Surfaces

| Path | Purpose | Approval Meaning |
|---|---|---|
| `.governance/Phase_Gates/` | Human-readable gate packages | Narrative evidence; approval depends on PM/PO sign-off |
| `.governance/Cross_Cutting/` | Risk, SoA, evidence index, crosswalks | Draft until reviewed/approved |
| `docs/verification/` | Verification artifacts | Evidence records, not approvals unless explicitly stated |
| `docs/decisions/` | Decision records | Proposed/accepted/superseded decision history |

## Known Gaps / Open Questions

| ID | Gap / Question | Owner | Required Before |
|---|---|---|---|
| GAP-001 | [Describe gap] | [Owner] | [Gate/task] |

## Non-Actions Without Approval

Do not perform the following without explicit authority:

- Mark any phase gate approved.
- Resume implementation work while the active implementation gate is closed.
- Delete/reset/rewrite git history.
- Push to a remote or change repository visibility/settings unless approved.
- Treat scaffolded/template artifacts as project-approved evidence.

## Fresh-Session Restart Prompt

When handing off to a new session, summarize:

```text
You are taking over [Project Name]. Start by reading PROJECT.md, docs/handoff/documentation-map.md, docs/handoff/project-continuation-guide.md, orchestration/system_spec.md, the active coordination file, directives, .governance/Phase_Gates/, and orchestration/tasks.md. Verify git status. Do not write to implementation paths until the active gate is approved by the PM/PO. Continue from [specific task/gate] and preserve evidence in docs/verification/.
```
