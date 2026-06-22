#!/usr/bin/env python3
"""Deterministic helper for 15-agent task orchestration and phase-gate checks."""
import pathlib, re, sys
ROOT=pathlib.Path.cwd(); TASKS_FILE=ROOT/'orchestration/tasks.md'
ACCOUNTABLE=["Requirements BA","User Story BA","UI/UX Designer","Architecture SE","Database Engineer","Backend Developer","Frontend Developer","Pipeline DevOps","Performance DevOps","QA Engineer","Automation Test Engineer","Scrum Master","Program Analyst","Documentation SE","Security & Compliance Officer"]
DONE={'Done','Complete','Completed','Approved'}; OPEN={'Ready','Ready to Start','Backlog','Pending'}
FIELDS=['Task ID','Phase','Status','Owner Agent','Required Inputs','Dependencies','Acceptance Criteria','Evidence Required','Verification Command or Method','Handoff Target','Gate Impact']
def parse_tasks(txt):
    chunks=re.split(r'(?=^####\s+)',txt,flags=re.M); tasks=[]
    for c in chunks:
        m=re.match(r'####\s+([^:\n]+):?\s*(.*)',c)
        if not m: continue
        t={'Task ID':m.group(1).strip(),'Title':m.group(2).strip(),'raw':c}
        for f in FIELDS:
            mm=re.search(rf'\*\*{re.escape(f)}\*\*:\s*(.*)',c)
            if mm: t[f]=mm.group(1).strip()
        tasks.append(t)
    return tasks
def deps_complete(task,tasks):
    deps=task.get('Dependencies','None')
    if deps.lower() in ('none','n/a',''): return True, []
    ids=re.findall(r'TASK-\d+',deps); byid={t['Task ID']:t for t in tasks}; incomplete=[]
    for d in ids:
        if byid.get(d,{}).get('Status','') not in DONE: incomplete.append(d)
    return not incomplete, incomplete
def gate_ok(task):
    impact=task.get('Gate Impact','').lower(); phase=task.get('Phase','')
    if 'advance' not in impact and 'gate' not in impact: return True, ''
    gate_dir=ROOT/'.governance/Phase_Gates'
    approved=False
    if gate_dir.exists():
        for p in gate_dir.glob('**/*.md'):
            txt=p.read_text(errors='ignore')
            explicit_approval = re.search(r'(?im)^\s*(decision|approval state)\s*:\s*approved\s*$', txt) or '| Approved |' in txt
            has_security = 'Security & Compliance Officer' in txt
            has_evidence = 'docs/verification/' in txt or '.governance/' in txt
            if explicit_approval and has_security and has_evidence and 'Not Approved' not in txt:
                approved=True
                break
    return approved, f"phase gate evidence required for {phase}; explicit Approved decision, evidence path, and Security & Compliance Officer review are required"
def prompt(task):
    owner=task.get('Owner Agent','Unassigned')
    return f"""NEXT FACTORY TASK: {task['Task ID']} - {task.get('Title','')}
Owner Agent: {owner}
Phase: {task.get('Phase','')}
Status: {task.get('Status','')}
Required Inputs: {task.get('Required Inputs','')}
Acceptance Criteria: {task.get('Acceptance Criteria','see task board')}
Evidence Required: {task.get('Evidence Required','docs/verification/<task-id>/verify.md')}
Verification Command or Method: {task.get('Verification Command or Method','document objective verification')}
Handoff Target: {task.get('Handoff Target','Scrum Master')}

Instructions:
1. Confirm your SOUL and runtime TOML before acting.
2. Validate upstream inputs and dependencies; stop if missing.
3. Execute only this task scope.
4. Produce required evidence, including verify artifact and handoff record.
5. Update evidence index; do not mutate task status without evidence.
6. If this affects a gate, include Security & Compliance Officer review.
"""
def main():
    txt=TASKS_FILE.read_text(); tasks=parse_tasks(txt)
    for t in tasks:
        if t.get('Status','') in OPEN or 'Ready to Start' in t.get('raw',''):
            if t.get('Owner Agent','Unassigned').strip('[]') not in ACCOUNTABLE:
                print(f"REFUSAL: unknown accountable owner for {t['Task ID']}: {t.get('Owner Agent')}"); return 2
            ok, missing=deps_complete(t,tasks)
            if not ok: print(f"REFUSAL: dependencies incomplete for {t['Task ID']}: {', '.join(missing)}"); return 2
            gok,msg=gate_ok(t)
            if not gok: print('REFUSAL: '+msg); return 2
            print(prompt(t)); return 0
    print('No ready tasks found.'); return 0
if __name__=='__main__': sys.exit(main())
