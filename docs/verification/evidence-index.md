# Verification Evidence Index

> Template status: gap-labeled scaffold. Use this index to point reviewers to append-only verification records in `docs/verification/` and formal governance evidence in `.governance/`.

| Evidence ID | Date | Artifact | Claim Supported | Verification Method | Hash / Commit | Status |
|---|---|---|---|---|---|---|
| EV-001 | [YYYY-MM-DD] | [path] | [claim] | [command/tool/review] | [hash/commit] | Draft / Gap |

## Evidence Quality Rules

- Prefer recorded command output, hashes, commit SHAs, API responses, screenshots, or signed reviews over narrative assertions.
- Do not fabricate test results, approvals, signatures, or artifact completeness.
- Label unverifiable claims as assumptions or gaps.
- Status `Verified` is reserved for evidence the Human Director has reviewed; cite the review or gate record, e.g. `Verified (Human Director review, <record>)`. An agent lists its own artifacts as `Generated — awaiting Human Director review`. The governed factory flags any dispatched run that adds a Verified label.
- Keep verification records append-only where practical; if superseded, link the newer record.
