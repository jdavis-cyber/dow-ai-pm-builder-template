# Task Board - 15-Agent Factory Orchestration

## Sprint Information
**Sprint**: [Sprint Number]  
**Sprint Goal**: [High-level objective for this sprint]  
**Gate Status**: Draft / Not Approved

## Schema
See `orchestration/task-schema.md`. Task status is not approval evidence.

## Backlog

#### TASK-001: Discovery intake and readiness package
**Task ID**: TASK-001  
**Phase**: CPMAI Phase I  
**Status**: Ready  
**Owner Agent**: Requirements BA  
**Required Inputs**: PROJECT.md, PM/PO interview notes or explicit discovery request  
**Dependencies**: None  
**Acceptance Criteria**: Requirements are measurable, compliance scope is classified, open gaps are labeled  
**Evidence Required**: `docs/verification/TASK-001/verify.md`; `directives/templates/agent-handoff-record.md` instance  
**Verification Command or Method**: Requirements BA self-check plus Scrum Master readiness review  
**Handoff Target**: User Story BA; Scrum Master  
**Gate Impact**: none

#### TASK-002: Security and compliance gate review scaffold
**Task ID**: TASK-002  
**Phase**: CPMAI Phase I  
**Status**: Pending  
**Owner Agent**: Security & Compliance Officer  
**Required Inputs**: TASK-001 evidence; standards applicability record  
**Dependencies**: TASK-001  
**Acceptance Criteria**: Applicability is explicit; ISO 27701 remains Reference Needed / Not Authoritatively Mapped; product overlays are conditional  
**Evidence Required**: `docs/verification/TASK-002/verify.md`; `.governance/security-compliance/override-register.md` if needed  
**Verification Command or Method**: Compliance review against `directives/factory-governance-scope.md`  
**Handoff Target**: Scrum Master; Program Analyst  
**Gate Impact**: blocks Gate 1 until compliance review exists
