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

`Requires Authority` is the structured authority declaration the dispatcher
checks before dispatch. Use `none`, or a comma-separated list of:
`implementation`, `source-admission`, `external-write`, `tracker-write`,
`deploy`, `real-data`, `cdrl-submit`, `risk-accept`, `control-close`.
Free text elsewhere in the task never adds or removes an authority check.

Valid owner agents are the 15 accountable agents in `.agent/AGENT-ROSTER.md`.
