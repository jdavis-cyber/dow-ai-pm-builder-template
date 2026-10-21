# Task Board Schema

Each machine-readable task block must use this Markdown shape:

#### TASK-001: Task title
**Task ID**: TASK-001  
**Phase**: CPMAI Phase I  
**Status**: Ready  
**Owner Agent**: Requirements BA  
**Required Inputs**: paths or `None`  
**Dependencies**: None  
**Acceptance Criteria**: measurable criteria  
**Evidence Required**: `docs/verification/TASK-001/verify.md`  
**Verification Command or Method**: command or review method  
**Handoff Target**: Scrum Master  
**Gate Impact**: none / blocks gate / advances gate  
**Requires Authority**: none  
**Human Gate**: no  
**Plan**: `docs/verification/TASK-001/plan.md` (required when Human Gate is yes)

`Requires Authority` is the structured authority declaration the dispatcher
checks before dispatch. Use `none`, or a comma-separated list of:
`implementation`, `source-admission`, `external-write`, `tracker-write`,
`deploy`, `real-data`, `cdrl-submit`, `risk-accept`, `control-close`.
Free text elsewhere in the task never adds or removes an authority check.

Valid owner agents are the 15 accountable agents in `.agent/AGENT-ROSTER.md`.

`Human Gate: yes` puts the task behind a written, approved plan
(plan-before-build). Its statuses run:

1. `Ready`: the dispatcher sends a plan-only packet; the agent writes the plan
   at `Plan` from `directives/templates/implementation-plan.md`, sets the status
   to `Planned`, and stops. The plan-only run carries no authority.
2. `Planned`: waiting for the Human Director. The Director reviews the plan and
   runs `python3 automation/gatekeeper.py approve-plan TASK-001 <plan path>`,
   which records a signed approval of that exact plan, then sets `Plan Approved`.
3. `Plan Approved`: dispatched for implementation, with the normal authority
   checks. Editing the plan after approval invalidates it.

A Phase IV–VI task whose Gate Impact is not `none` must have `Human Gate: yes`.
