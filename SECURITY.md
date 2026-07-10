# Security policy

## Reporting a vulnerability

If you find a security issue in this template — a flaw in the automation
scripts, a governance control that can be bypassed in a way its documentation
says it cannot, or leaked sensitive material — please report it privately:

- **Preferred:** GitHub → *Security* tab → *Report a vulnerability*
  (private vulnerability reporting).
- Please do not open a public issue for anything sensitive.

You can expect an acknowledgment within a few days. This is a solo-maintained
portfolio project, not a staffed product; there is no bug-bounty program.

## Incident communication to template users

If a confirmed issue affects people who have already cloned or adopted this
template — a governance control that does not work as documented, a defect in
the automation scripts, or leaked sensitive material — it is communicated
outward, not just fixed:

1. **GitHub Security Advisory** for anything security-relevant (the
   repository's *Security* → *Advisories* page is the canonical channel).
2. **CHANGELOG.md entry** naming the defect and the corrective change, so the
   record survives in-repo.
3. **README or affected-document correction** in the same change, when the
   incident is a documentation-vs-reality gap.

There is no user registry and no push notification channel: watchers and
adopters are expected to follow the repository. This is stated as a known
limitation, not hidden.

**Self-detected violations (operators of generated projects):** when the
factory's own detective stops report a violation (a run-result record with
`outcome: violation`), the operator records the disposition in
`.governance/security-compliance/override-register.md` and communicates it
through their organization's incident process. Violations that trace back to
a defect in this template should also be reported upstream via the path
above.

## Scope notes

- This repository is a **template**. It contains no deployed services, no
  credentials, and no runtime infrastructure of its own.
- The governance model is **fail-closed by design**: generated projects start
  in *Draft / Not Approved*, and the dispatcher must stop on authority
  boundaries (`automation/gatekeeper.py`, `.governance/gate_state.json`).
  Reports that demonstrate a way to defeat those stops from inside the
  documented workflow are exactly the kind of report this policy is for.
- Adapter commands (`FACTORY_ADAPTER_COMMAND`) execute whatever the operator
  configures. Protecting the operator's own shell environment is out of scope;
  the template never ships a default adapter.
