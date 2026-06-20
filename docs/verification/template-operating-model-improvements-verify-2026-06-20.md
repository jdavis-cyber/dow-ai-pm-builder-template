# Template Operating-Model Improvements Verification

## Artifact Status

| Field | Value |
|---|---|
| Status | Verified |
| Approval State | Not Approved |
| Evidence Type | Verified |
| Owner | Lliam-GOV |
| Last Updated | 2026-06-20 |

## Scope

Repository: `jdavis-cyber/dow-ai-pm-builder-template`  
Local workspace: `/Users/just_jerome/Documents/Program & Project Management/dod-lclm-platform-governance-restart`  
Branch: `feat/single-repo-operating-model`  
Baseline before branch: `75940d0e31d7af3f4c6e10c150a1a7b1a093e799`

## Objective

Implement the template improvements required for the single-authoritative-repo operating model:

1. Protect conventional implementation paths, not only `execution/`.
2. Make the template explicitly describe one repo as the source + governance + decisions + evidence + handoff package.
3. Add handoff, decision, verification, artifact-status, and repo-controls scaffolds.
4. Ensure `automation/init_project.py` stamps those scaffolds into new project repos.
5. Verify the gatekeeper and instantiation path before pushing for review.

## Files Changed / Added

Expected changed files:

```text
CLAUDE.md
CODEX.md
DEMO.md
GEMINI.md
INSTALL.md
PROJECT.md
README.md
automation/gatekeeper.py
automation/init_project.py
directives/structural-integrity-protocol.md
.governance/README.md
docs/decisions/ADR-000-template.md
docs/handoff/documentation-map.md
docs/handoff/project-continuation-guide.md
docs/handoff/project-instantiation-checklist.md
docs/handoff/repo-controls-checklist.md
docs/templates/artifact-status-block.md
docs/verification/evidence-index.md
docs/verification/template-operating-model-improvements-verify-2026-06-20.md
```

## Verification Evidence

Command bundle executed from template workspace:

```text
BRANCH
feat/single-repo-operating-model
STATUS
## feat/single-repo-operating-model
 M CLAUDE.md
 M CODEX.md
 M DEMO.md
 M GEMINI.md
 M INSTALL.md
 M PROJECT.md
 M README.md
 M automation/gatekeeper.py
 M automation/init_project.py
 M directives/structural-integrity-protocol.md
?? .governance/README.md
?? docs/decisions/
?? docs/handoff/
?? docs/templates/
?? docs/verification/evidence-index.md
PY_COMPILE
OK
GATEKEEPER_SRC_BLOCK
exit=2
Lock 0 (spec validation) is UNKNOWN. Resolve placeholders in the system spec before writing to gated implementation paths.
GATEKEEPER_DOCS_ALLOW
exit=0
GATEKEEPER_COMPOSE_BLOCK
exit=2
Lock 0 (spec validation) is UNKNOWN. Resolve placeholders in the system spec before writing to gated implementation paths.
INIT_PROJECT_SMOKE
▶ Instantiating project 'sample-project' from template...
✔ Project created: /private/tmp/dow-template-init-test-2/sample-project
✔ Template provenance: v4.0.0-5-g75940d0 (75940d0e31d7af3f4c6e10c150a1a7b1a093e799)
✔ Fresh git repo with initial commit; agent bundle materialized

Next: open /private/tmp/dow-template-init-test-2/sample-project in your AI coding agent (Claude Code, Codex, or Gemini)
  and instruct: "Initialize the project and begin Sprint Zero."
INIT_ARTIFACTS_OK
```

## Interpretation

- `automation/gatekeeper.py` and `automation/init_project.py` compile successfully.
- Closed-gate writes to `src/example.py` are blocked.
- Closed-gate writes to `docker-compose.yml` are blocked.
- Discovery/evidence writes to `docs/verification/example.md` are allowed.
- `automation/init_project.py` creates a fresh project repo and includes the new single-repo/handoff/decision/governance scaffolds.

## Non-Actions

- No template `main` merge was performed.
- No phase gate was marked approved.
- No project-specific LCLM source code was modified by this template change.
- No history rewrite or force operation was performed.
