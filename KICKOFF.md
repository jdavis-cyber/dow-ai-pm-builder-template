# New Project Kickoff Protocol

## Canonical operator phrase

```text
Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.
```

That phrase is intentionally sufficient. Operators should not have to front-load the project name, mission, objective, inputs, files, links, or governance caveats in the kickoff prompt. The factory must gather those details through Sprint Zero / Phase 0 discovery and the interview sequence.

## Required factory behavior

When the canonical operator phrase is received, the agent/factory must:

1. Verify the DoW AI PM Builder Template is healthy before creating or modifying a project workspace.
2. Ask only for the minimum information needed to instantiate the workspace if it is not already known — normally the `project name/path` or permission to use a temporary kebab-case working name.
3. Instantiate the project from the template once a safe project name/path is available.
4. Materialize and validate the full 15 accountable-agent runtime, including mandatory Security & Compliance Officer participation.
5. Begin Sprint Zero / Phase 0 using `orchestration/sprint-zero-playbook.md`.
6. Use the interview process to elicit and record the project name, mission, objectives, requirements, supplied inputs, files, links, constraints, stakeholders, external systems, and authority boundaries.
7. Keep generated artifacts marked Draft / Not Approved until an explicit phase-gate decision is recorded.
8. Prepare the Gate 1 readiness package and stop at Gate 1 readiness unless explicit authority is given to proceed further.

## Discovery ownership

The interview owns discovery details. Do not require the operator to paste a long kickoff prompt containing fields the factory is supposed to discover. If details are missing, ask them during the appropriate Sprint Zero interview step and record them in the system specification, task board, decision log, and evidence index as applicable.

## Boundaries that remain in force

- Do not begin implementation during kickoff.
- Do not claim Gate 1 approval, production readiness, product compliance, CDRL completion, risk acceptance, or control closure without explicit evidence and authority.
- Do not fabricate requirements, framework mappings, evidence, test results, approvals, or external-system state.
- Treat the 136 VoltAgent packages as specialization/capability packages mapped to accountable owners, not as peer accountable agents.
- Keep factory-governance evidence distinct from product-governance evidence.
- Keep ISO/IEC 27701 gap-labeled / reference-needed unless authoritative source mappings are supplied.
- Treat CMMC, FedRAMP, HIPAA, SOC 2, and similar overlays as conditional product-specific overlays only.

## Minimal fallback if context is insufficient

If the operator gives only the canonical phrase and no project name/path is known, respond with exactly the next required question, for example:

```text
Understood. I’ll start project initiation under the DoW AI PM Builder Template. What project folder/name should I use? If you do not have one yet, I can assign a temporary kebab-case working name.
```

After that, continue with template validation, instantiation, runtime validation, and the Sprint Zero interview flow.
