# Repository Controls Checklist

> Template status: scaffold. Use this checklist before relying on a GitHub/Git remote for governed project work.

## Artifact Status

| Field | Value |
|---|---|
| Status | Draft |
| Approval State | Not Approved |
| Evidence Type | Template Scaffold |
| Owner | Pipeline DevOps / Scrum Master |
| Last Updated | [YYYY-MM-DD] |

## Required Evidence

Record command/API output in `docs/verification/repo-controls-verify-YYYY-MM-DD.md`.

| Control | Required Check | Result | Evidence Location |
|---|---|---|---|
| Remote identity | `git remote -v` points to intended repo | [TBD] | [path] |
| Visibility | Private/public matches authorization | [TBD] | [path] |
| Default branch | Default branch is intentional, usually `main` | [TBD] | [path] |
| Branch protection/rulesets | Direct pushes, force pushes, and unreviewed merges constrained where plan allows | [TBD] | [path] |
| Merge strategies | Allowed strategies match governance preference | [TBD] | [path] |
| Delete branch on merge | Enabled unless retention required | [TBD] | [path] |
| Issues/projects/wiki | Enabled/disabled intentionally | [TBD] | [path] |
| CODEOWNERS | Considered for review routing | [TBD] | [path] |
| CI/workflows | Required checks identified or residual risk documented | [TBD] | [path] |
| Secrets | No secrets committed; required GitHub secrets named but values not disclosed | [TBD] | [path] |

## Private Repo Branch Protection Note

Some GitHub plans restrict branch protection/rulesets for private repositories. If GitHub blocks protection on a private repo, do not make the repo public without explicit approval. Record the limitation as residual risk and propose options:

1. Upgrade/enable a plan that supports private branch protection.
2. Keep the repo private and use procedural controls until plan support exists.
3. Make the repo public only if disclosure is explicitly approved and appropriate.

## Non-Actions Without Approval

- Do not change repo visibility.
- Do not force-push.
- Do not delete branches/tags.
- Do not add/remove collaborators or change access.
- Do not publish source or evidence to a remote unless that upload is authorized.
