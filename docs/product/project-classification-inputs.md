# Project Classification Inputs

## Purpose

This note defines the minimum project-classification answers that must be captured before `subagents/install-config.json` can be authored or consumed. It exists to stop downstream teams from inferring regulated scope, agent activation, or startup behavior from incomplete discovery.

## Required Inputs

| Key | Required Answer | Allowed Values | Why It Exists |
|-----|-----------------|----------------|---------------|
| `project_type` | Yes | `standard`, `ai-ml`, `dod-regulated`, `hipaa` | Establishes the primary delivery and governance class of the project |
| `languages` | Yes | Explicit language list | Restricts language-specific agent packages to the actual stack |
| `platforms` | Yes | Explicit platform list | Restricts platform-specific packages to the actual delivery surface |
| `requires_accessibility` | Yes | `true`, `false` | Determines whether accessibility specialists and checks are mandatory |
| `requires_dod_controls` | Yes | `true`, `false` | Separates DoD or federal control obligations from general project type labels |
| `requires_iso42001` | Yes | `true`, `false` | Declares whether AI management system controls are mandatory at launch |

## Business Rules

- `project_type = dod-regulated` requires `requires_dod_controls = true`.
- `requires_dod_controls = true` requires regulated overlays and Security and Compliance Officer participation.
- `project_type = ai-ml` does not automatically force `requires_dod_controls`; federal and defense scope must be answered separately.
- `requires_iso42001` must be answered explicitly for every `ai-ml` project.
- Empty, contradictory, or inferred answers are invalid and must block install-profile generation.

## Decision Authority

- The Human Director owns the mission, regulated-scope declaration, and outcome definition.
- The Requirements BA owns the capture and validation of these answers.
- The Scrum Master owns escalation when answers are missing or contradictory.
- Architecture SE and DevOps consume the approved answers and may not redefine them during implementation.

## Acceptance Standard

The classification input set is acceptable only when:

1. The primary outcome is measurable.
2. User roles and authority boundaries are explicit.
3. Compliance scope is stated in plain terms and not inferred from project name alone.
4. The six required input keys above are fully answered.
5. Any conflict between delivery scope and compliance scope is escalated before install work starts.
