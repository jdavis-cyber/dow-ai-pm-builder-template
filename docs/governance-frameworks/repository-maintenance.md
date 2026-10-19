# Repository maintenance scope

This note describes maintenance of the source template. A copy is included in
generated projects so their scope and navigation links remain self-contained;
their project-specific gate and evidence requirements remain separate.

Ordinary maintenance of this template uses code review, build and regression
checks. It does not require adopting an organizational management system or
maintaining duplicate assurance documents for the repository itself.

## Optional references

The control matrix, statement of applicability, factory risk register,
factory objectives, model-supplier criteria and example AI policy remain
available as historical self-assessment and adoption references. They are not
mandatory files, required wording or recurring approval records for a passing
build. Copying them does not establish organizational policy or certification.
The standards crosswalk likewise has no exact-phrase CI requirement.

No files were deleted: existing links, evidence and provenance remain useful.
The references and scope directive now explain this optional status. Historical
changelog entries describe earlier behavior, not current CI requirements.

## Checks and behavior retained

The `whole-template` job still runs template validation, project-generation
smoke testing and the full regression suite. Roster, specialization ownership,
runtime manifests, specification/task structure, dispatcher and authority
checks remain. The metrics script and its unreadable-record/violation tests,
security-reporting checks, licenses and upstream attribution are retained.

The generated project's `.governance/gate_state.json`, gatekeeper, phase-gate
records, task evidence and security/approval behavior are untouched. These are
part of the product's operating contract. Relaxing them would change application
behavior and requires a separate decision; this cleanup does not do that.
No branch protections, required-check names or repository settings change.

## Validation

```sh
python3 automation/validate_template.py
python3 automation/smoke_test_template.py
python3 -m unittest discover -s tests
```

Regression tests also validate a disposable template without the six optional
references and with different crosswalk prose. A second test removes an
authority token in a disposable copy and confirms validation still rejects it.
