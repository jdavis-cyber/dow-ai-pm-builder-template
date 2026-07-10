# Factory Risk Register — DoW AI PM Builder Template

**Scope and honesty statement (read first).** This register records risks of
operating the factory *itself* — the template's multi-agent orchestration,
governance automation, and supplier model runtimes. It is a **repo-level
self-assessment**, not a certification claim, and not a substitute for the
risk register an adopting organization's management system must maintain
(ISO/IEC 42001 clause 6.1 attaches to the adopter; this register supplies the
factory-level input to it). Product/engagement risks (CUI handling, FedRAMP,
HIPAA and similar overlays) are conditional per
`directives/factory-governance-scope.md` and are deliberately absent here.

Scoring: Likelihood (L) × Impact (I), each 1–3. 1–2 Low · 3–4 Medium · ≥6 High.
Review cadence: re-verified at every factory version bump and at least
annually, per `docs/governance-frameworks/factory-ai-policy.md`.

| ID | Risk | Category | L | I | Score | Level | Treatment / operating mechanism | Evidence |
|----|------|----------|---|---|-------|-------|--------------------------------|----------|
| FR-01 | Artifact inconsistency / output error — agents produce outputs inconsistent with upstream artifacts or factually wrong | Operational | 2 | 2 | 4 | Medium | Lock 0 spec validation before build; phase-gate human review; whole-template validation + CI | `automation/validate_spec.py`, `.governance/Phase_Gates/`, `.github/workflows/validate.yml` |
| FR-02 | Compliance-enforcement failure — the Security & Compliance Officer agent fails to enforce factory-baseline frameworks due to prompt drift or hallucination | Governance | 1 | 3 | 3 | Medium | Gate approval is a human decision against evidence (agent output is input, not authority); officer is non-removable; post-dispatch detective stops backstop the agent layer | `automation/gatekeeper.py`, `subagents/install-config.json` (mandatory agents), `automation/governed_factory.py` (`post_dispatch_checks`) |
| FR-03 | Bias in generated content — bias injected into persona generation, stakeholder identification, or risk framing | Ethical | 2 | 2 | 4 | Medium | Phase-gate human review before artifacts leave Draft; measurement gap acknowledged (see SoA, MEASURE 2) | `.governance/Phase_Gates/`, `docs/governance-frameworks/factory-soa.md` |
| FR-04 | Model-provider API outage / rate limits halt operations | Supplier | 2 | 2 | 4 | Medium | Provider-neutral dispatcher — any of the three runtimes (or another shell adapter) can execute; on-demand local operation, no persistent service | `automation/governed_factory.py`, `factory.config.example.json`, `docs/governance-frameworks/model-supplier-criteria.md` |
| FR-05 | Agent autonomy drift — a multi-agent loop enters an unintended autonomous cycle or invents tasks outside boundaries | Technical | 1 | 2 | 2 | Low | Dispatch is per-task with an explicit packet of authorities and non-authorities; open-task redispatch guard; fail-closed stop conditions | `docs/verification/factory-runs/` packets, `automation/governed_factory.py`, `tests/test_governance_gates.py` |
| FR-06 | False-positive compliance halt — hallucinated non-compliance hard-stops a phase gate and stalls work | Operational | 2 | 3 | 6 | High | Gate decisions are human-made against cited evidence; the override register makes justified exceptions a recorded, visible event rather than a silent bypass | `.governance/security-compliance/override-register.md`, `directives/ai-governance-framework.md` (Fail-Closed Rule) |
| FR-07 | Configuration drift — a specialization package attempts to weaken a SOUL's hardcoded governance requirements | Cybersecurity | 1 | 3 | 3 | Medium | SOUL-over-TOML precedence in the governance wrapper; 156-entry ownership map; validator enforces roster and full ownership coverage | `subagents/GOVERNANCE_WRAPPER.md`, `subagents/specialization-ownership-map.json`, `automation/validate_template.py` |
| FR-08 | Upstream spec ambiguity — unresolved TBDs cascade into the 15-agent workflow as widespread output errors | Operational | 2 | 2 | 4 | Medium | Lock 0 spec linter blocks ambiguous specs; Sprint Zero discovery interview resolves context before build | `automation/validate_spec.py`, `KICKOFF.md`, `directives/director-interview-protocol.md` |
| FR-09 | Premature externally-facing release — output leaves Draft state without authorization | Reputational | 1 | 3 | 3 | Medium | Fail-closed authority store: deployment, external writes, and control closure ship denied and require explicit human grant | `.governance/gate_state.json`, `automation/gatekeeper.py`, `tests/` (authority tests) |
| FR-10 | Compliance-obligation misidentification — the factory (or its docs) claims a framework that does not apply, or misses one that does | Regulatory | 2 | 2 | 4 | Medium | Two-track scope doctrine (baselines vs conditional overlays); claims-integrity fence keeps unmapped frameworks labeled "Reference Needed" | `directives/factory-governance-scope.md`, `directives/templates/standards-crosswalk-matrix.md` |
| FR-11 | Documentation drift — factory-describing documents fall behind the factory's actual mechanisms and counts | Governance | 2 | 2 | 4 | Medium | Standing rule: documentation re-verified at every version bump with a recorded verified-SHA; counts regenerated from commands, never inherited; CHANGELOG discipline | `CHANGELOG.md`, cohesion-audit record (2026-07-10), this file's verification stamp |
| FR-12 | Pre-dispatch misclassification — keyword-based action inference mislabels a task's authority requirements | Technical | 2 | 2 | 4 | Medium | Known limitation stated in README; post-dispatch git audit detects unauthorized protected-source writes regardless of classification | `README.md` (Known limitations), `automation/governed_factory.py` (`post_dispatch_checks`), `tests/test_governance_gates.py` |
| FR-13 | Supply-chain exposure — vendored specialization packages or CI dependencies change or carry defects upstream | Supplier | 1 | 2 | 2 | Low | Full attribution and license notice; every vendored package owner-mapped; Dependabot alerts + security updates on the repo; supplier criteria govern runtime providers | `THIRD_PARTY_LICENSES.md`, `subagents/specialization-ownership-map.json`, `docs/governance-frameworks/model-supplier-criteria.md` |

## Known gaps (stated on purpose)

- Residual-risk acceptance is an **adopter decision**: this register proposes
  treatments and shows the operating mechanism, but formal risk acceptance
  requires an accountable owner inside an operating organization.
- Bias (FR-03) is mitigated by human review, not measured; no factory-level
  bias metric exists (accepted at template scope — measurement attaches to a
  generated product with real users and data).
- Likelihood/impact scores are the maintainer's engineering judgment, not
  actuarial data; adopters should re-score against their own context.

*Maintained by: Human Director. Update this register in the same change that
adds, removes, or weakens any mechanism it cites. Verified against commit
`8991e57` (2026-07-10); re-verify at every version bump.*
