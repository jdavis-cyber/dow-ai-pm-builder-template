# Standards Crosswalk Matrix — Gap-Labeled Scaffold

> Scaffold status: Draft / Not Approved. Do not treat blank or placeholder rows as completed mappings.

## Framework Status

| Framework | Status | Mapping Rule |
|---|---|---|
| CPMAI | Baseline factory-governance lifecycle | Map to phase artifacts and gate records |
| ISO/IEC 42001 | Baseline factory-governance AIMS target | Map only where clause/source reference is confirmed |
| NIST AI RMF | Baseline AI risk overlay | Map to GOVERN/MAP/MEASURE/MANAGE evidence |
| ISO/IEC 27001 | Crosswalk candidate | Available for authoritative mapping when source clauses are supplied/confirmed |
| ISO/IEC 27701 | Reference Needed / Not Authoritatively Mapped | No authoritative clause mapping until full standard is available |

## Crosswalk Rows

| Topic | CPMAI | ISO/IEC 42001 | NIST AI RMF | ISO/IEC 27001 | ISO/IEC 27701 | Evidence Artifact | Status |
|---|---|---|---|---|---|---|---|
| Phase governance | Phase gate records | Reference required | GOVERN | Reference required | Reference Needed — Not Authoritatively Mapped | `.governance/Phase_Gates/` | Draft |
| Runtime accountability | Agent roster/manifest | Reference required | GOVERN | Reference required | Reference Needed — Not Authoritatively Mapped | `.agent/AGENT-ROSTER.md`, `.codex/agents/runtime-manifest.json` | Draft |
| Evidence integrity | Verification/evidence index | Reference required | MANAGE | Reference required | Reference Needed — Not Authoritatively Mapped | `docs/verification/evidence-index.md` | Draft |

Do not infer or fabricate mappings. Mark unverified mappings as `Reference required` or `Reference Needed`.
