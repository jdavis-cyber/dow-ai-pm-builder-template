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
