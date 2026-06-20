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
| Approved | Accepted by the required approval mechanism |
| Rejected | Reviewed and not accepted |
| Superseded | Replaced by a newer artifact or decision |
| Historical | Preserved for traceability; not current authority |

## Evidence Type Definitions

| Evidence Type | Meaning |
|---|---|
| Template Scaffold | Generic template starter material; never approval evidence by itself |
| Project-Specific | Populated for this project |
| Generated | Produced by a tool/agent and requires review before authority |
| Historical | Preserved from an earlier state for traceability |
| Verified | Supported by recorded command/API/tool output |

## Rule

A file's existence is not approval. An artifact is approved only when the relevant approval section, gate package, or signed/machine-readable approval mechanism says so.
