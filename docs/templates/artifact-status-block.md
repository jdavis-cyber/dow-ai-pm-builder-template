# Artifact Status Block Template

Use this block near the top of governance, decision, verification, and handoff artifacts.

```markdown
## Artifact Status

| Field | Value |
|---|---|
| Status | Draft / Proposed / Ready for Review / Approved / Rejected / Superseded / Historical |
| Approval State | Not Approved / Approved / Conditional / N/A |
| Evidence Type | Template Scaffold / Project-Specific / Generated / Historical / Verified |
| Owner | [Role] |
| Last Updated | [YYYY-MM-DD] |
```

## Status Definitions

| Status | Meaning |
|---|---|
| Draft | Work in progress; not ready for decision |
| Proposed | Ready for review but not accepted |
| Ready for Review | Complete enough for PM/PO/security review |
| Approved | Accepted by PM/PO sign-off |
| Rejected | Reviewed and not accepted |
| Superseded | Replaced by a newer artifact or decision |
| Historical | Preserved for traceability; not current authority |

## Evidence Type Definitions

| Evidence Type | Meaning |
|---|---|
| Template Scaffold | Generic template starter material; never approval evidence by itself |
| Project-Specific | Populated for this project |
| Generated | Produced by a tool or agent, including the command output it recorded; requires Human Director review before authority |
| Historical | Preserved from an earlier state for traceability |
| Verified | Reviewed and accepted by the Human Director; cite the review or gate record |

## Rule

A file's existence is not approval. An artifact is approved only when the relevant approval section or gate package says so.

Agents never label their own output Verified. They record it as Generated; the
Human Director marks it Verified after reviewing it. The governed factory flags
any dispatched run that adds a Verified label.
