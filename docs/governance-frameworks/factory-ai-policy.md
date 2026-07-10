# Factory AI Policy — The Factory's Own Use of AI

**Scope and honesty statement (read first).** This is the policy for how the
factory *itself* uses AI: multi-agent LLM orchestration that produces project
artifacts under repo-owned governance. It is a **repo-level self-assessment**
artifact, not a certification claim. An adopting organization's AI policy
(management-system level, with leadership approval and communication evidence)
sits above this one; on adoption, this policy becomes the factory-specific
annex beneath it, and any conflict resolves in favor of the adopter's policy.

## Policy statements

1. **Human authority is the ceiling.** AI agents draft, analyze, and execute
   scoped tasks; humans approve. Phase gates, deployment, external writes,
   risk acceptance, and control closure are human decisions enforced
   fail-closed by `.governance/gate_state.json` and `automation/gatekeeper.py`.
2. **Every AI action is attributable.** Work resolves to a named accountable
   role (15-agent roster) and, for autonomous dispatch, to a persisted task
   packet and run-result record.
3. **Fail closed, not open.** Missing evidence, ambiguous authority, or
   validation failure stops work. Exceptions exist only as recorded rows in
   the override register — never as silent bypasses.
4. **Claims must be verifiable.** Framework mappings, counts, and capability
   statements ship with evidence pointers and verification commands; unmapped
   frameworks stay labeled "Reference Needed" (claims-integrity fence).
   Fabricating compliance is prohibited.
5. **The factory trains no models and acquires no datasets.** It consumes
   operator-supplied project context and produces documents and code. If a
   generated *product* uses data or models, the product overlay doctrine
   applies (`directives/factory-governance-scope.md`), not this policy alone.
6. **Suppliers are chosen deliberately.** Runtime providers are assessed
   against `docs/governance-frameworks/model-supplier-criteria.md`; provider
   neutrality is maintained so no single supplier becomes a silent dependency.
7. **The factory documents itself honestly.** Known limitations are stated in
   README; risks in `factory-risk-register.md`; objectives and their
   measurement in `factory-objectives.md`; per-control dispositions in
   `factory-soa.md`. Documentation is re-verified at every version bump
   (verified-SHA rule).

## Alignment with other policies (A.2.3)

This policy operates alongside, and defers to where applicable:

- `SECURITY.md` — vulnerability reporting and incident communication.
- `directives/factory-governance-scope.md` — two-track compliance doctrine.
- `directives/ai-governance-framework.md` — fail-closed rule and evidence
  obligations.
- `LICENSE` and `THIRD_PARTY_LICENSES.md` — licensing and attribution.
- The adopting organization's AI, security, and quality policies on adoption.

## Review cadence and review log (A.2.4)

This policy is reviewed **at every tagged release or quarterly, whichever
comes first**, by the Human Director, for continuing suitability, adequacy,
and effectiveness. Reviews that change policy substance are recorded in
`CHANGELOG.md`; the review log below is updated even when no change is
needed, so staleness is detectable.

| Review date | Reviewer | Trigger | Outcome |
|-------------|----------|---------|---------|
| 2026-07-10 | Human Director | Initial adoption (assurance layer, AI-551) | Policy adopted; verified against the factory at commit `8991e57` |

## Known gaps (stated on purpose)

- There is no leadership-approval or communication evidence at template scope
  — clause-level policy governance (5.2, 7.4) attaches to the adopting
  organization.
- Policy enforcement against a *hostile* operator is out of scope: the
  operator owns the machine and the adapter. The policy governs the honest
  operating model, and the detective controls make deviations visible.

*Maintained by: Human Director. Verified against commit `8991e57`
(2026-07-10); re-verify at every version bump.*
