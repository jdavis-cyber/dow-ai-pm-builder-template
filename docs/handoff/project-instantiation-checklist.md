# Project Instantiation Checklist

> Template status: scaffold. Complete this checklist when creating a new governed project from the template or when normalizing an existing project into the single-repo operating model.

## Artifact Status

| Field | Value |
|---|---|
| Status | Draft |
| Approval State | Not Approved |
| Evidence Type | Template Scaffold |
| Owner | Scrum Master |
| Last Updated | [YYYY-MM-DD] |

## 0. Boundary and Authority

- [ ] Confirm the target project repo/path.
- [ ] Confirm whether remote repo creation/push is authorized.
- [ ] Confirm whether the repo contains sensitive/customer/regulated data.
- [ ] Confirm branch protection/review expectations.
- [ ] Confirm the active human PM/PO or Director approval mechanism.

## 1. Template Provenance

- [ ] Record template source URL.
- [ ] Record template commit SHA.
- [ ] Record instantiation timestamp from the live system.
- [ ] Preserve `TEMPLATE_PROVENANCE.md` or equivalent in the project repo.
- [ ] Record any deviations from the template in `docs/decisions/`.

## 2. Single-Repo Layout

- [ ] Confirm the project repo contains or will contain implementation source.
- [ ] Confirm source/governance separation by folder, not by separate repositories.
- [ ] Populate `docs/handoff/documentation-map.md`.
- [ ] Populate `docs/handoff/project-continuation-guide.md`.
- [ ] Populate or create `.governance/README.md`.
- [ ] Confirm `docs/decisions/` exists for ADRs and governance decision records.
- [ ] Confirm `docs/verification/` exists for append-only evidence records.

## 3. Implementation Paths

Confirm the project's implementation surfaces and folder boundaries before implementation begins. These paths are held until the active phase gate is approved by the PM/PO.

Conventional implementation path prefixes:

```text
execution/
src/
app/
apps/
packages/
services/
database/
infrastructure/
.github/workflows/
```

Conventional implementation root/runtime files:

```text
docker-compose.yml
docker-compose.yaml
compose.yml
compose.yaml
Dockerfile
Containerfile
package.json
package-lock.json
pnpm-lock.yaml
yarn.lock
go.mod
go.sum
pyproject.toml
poetry.lock
requirements.txt
requirements-dev.txt
```

- [ ] Confirm these paths cover the actual implementation surfaces.
- [ ] Add project-specific implementation paths if needed.
- [ ] Record any path changes in `docs/decisions/`.
- [ ] Confirm implementation work begins only after the active phase gate is approved by the PM/PO.

## 4. Artifact Status Metadata

Every significant governance, decision, verification, and handoff artifact should include a status block:

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

- [ ] Status metadata present on gate packages.
- [ ] Status metadata present on decision records.
- [ ] Status metadata present on verification records where applicable.
- [ ] Scaffolded artifacts remain labeled as template scaffolds until populated and reviewed.

## 5. Repo Controls

- [ ] Repo visibility confirmed.
- [ ] Default branch confirmed.
- [ ] Branch protection/rulesets configured or residual risk documented.
- [ ] Merge strategies configured.
- [ ] CODEOWNERS considered for governance/security review.
- [ ] Issues/projects/wiki settings configured intentionally.
- [ ] Repo controls evidence recorded in `docs/verification/`.

## 6. Gate 1 Startup

- [ ] Read startup files.
- [ ] Verify `orchestration/system_spec.md` exists and has no placeholders before implementation.
- [ ] Create/refresh Mission Risk Profile.
- [ ] Create/refresh Governance Scope Statement.
- [ ] Create/refresh initial SoA / standards applicability.
- [ ] Create/refresh risk register entry set.
- [ ] Create Gate 1 package.
- [ ] Stop for PM/PO decision. Do not self-approve.
