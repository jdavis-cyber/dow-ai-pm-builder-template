# Model-Supplier Criteria — Selecting and Reviewing Runtime Providers

**Scope and honesty statement (read first).** The factory is provider-neutral:
governance lives in this repository, and any LLM runtime (Claude, Codex,
Gemini, or another shell adapter) executes tasks under it. This document
states the criteria an operator applies when selecting or re-reviewing a
model supplier for factory use. It is a **repo-level self-assessment**
artifact, not a certification claim and not a supplier contract. Formal
supplier management records (approvals, review evidence, contractual terms)
belong to the adopting organization's management system; this document is the
factory-level input to them.

## Selection criteria

| # | Criterion | What to check | Why it matters here |
|---|-----------|---------------|---------------------|
| 1 | Terms of service and license compatibility | Provider terms permit the intended use; output ownership is clear | Factory outputs become project artifacts; ambiguous output rights poison the evidence chain |
| 2 | Data-use commitments | Whether prompts/outputs are used for provider training; retention windows; opt-out mechanics | Project text is operator-supplied context; it must not silently become supplier training data |
| 3 | Model documentation and change notice | Provider publishes model/system cards, version identifiers, and deprecation/change notices | Factory behavior can shift under an unchanged config (register FR-17); documented capabilities and change awareness — or version pinning — are required |
| 4 | Availability and status transparency | Public status page; documented rate limits | Dispatch halts are an operational risk; the provider-neutral design is the fallback, not a substitute for knowing supplier health |
| 5 | Security posture documentation | Published security/compliance documentation appropriate to the operator's context | The supplier is inside the factory's trust boundary during a run |
| 6 | Capability fit for governed execution | Follows structured instructions, respects stop conditions, usable through a scriptable CLI/API adapter | The dispatcher requires an adapter that can be halted and audited; a runtime that can't be scripted can't be governed here |
| 7 | Exit strategy | A second qualified runtime is configured or configurable | Provider neutrality is this factory's supplier-concentration treatment; it only works if the second adapter is actually exercised |

## Review cadence and triggers

- Re-review a supplier at every factory **version bump**, and immediately on:
  a material model-version change, a terms-of-service change affecting data
  use, or a supplier-caused dispatch failure recorded in a run result.
- Record the review outcome in the adopting organization's supplier records;
  at repo level, note material supplier changes in `CHANGELOG.md`.

## Bridge to organization-level supplier records

An adopting organization operating a management system (e.g., ISO/IEC 42001
A.10.3) should hold one supplier record per runtime provider, covering the
criteria above plus contractual and commercial terms. This document defines
*what the factory needs from a supplier*; the organization's records prove
*that a specific supplier was assessed and approved*. Keep the two linked:
the supplier record should cite this file, and material criteria changes here
should trigger a supplier-record review there.

## Known gaps (stated on purpose)

- The template ships **no supplier assessments** — it cannot know which
  providers an operator will configure. Criteria without applied assessments
  are a method, not evidence.
- Vendored specialization packages are a separate supply-chain surface,
  handled by `THIRD_PARTY_LICENSES.md` and the ownership map, not by this
  document.

*Maintained by: Human Director. Verified against commit `8991e57`
(2026-07-10); re-verify at every version bump.*
