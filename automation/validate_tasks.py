#!/usr/bin/env python3
import pathlib, re, sys
REQUIRED = ['Task ID','Phase','Status','Owner Agent','Required Inputs','Dependencies','Acceptance Criteria','Evidence Required','Verification Command or Method','Handoff Target','Gate Impact']
ACCOUNTABLE = {"Requirements BA","User Story BA","UI/UX Designer","Architecture SE","Database Engineer","Backend Developer","Frontend Developer","Pipeline DevOps","Performance DevOps","QA Engineer","Automation Test Engineer","Scrum Master","Program Analyst","Documentation SE","Security & Compliance Officer"}

def task_blocks(txt):
    return [c for c in re.split(r'(?=^####\s+)', txt, flags=re.M) if c.startswith('#### ')]

def validate(path):
    p = pathlib.Path(path)
    txt = p.read_text()
    ok = True
    blocks = task_blocks(txt)
    if not blocks:
        print('ERROR: no task blocks found')
        ok = False
    for block in blocks:
        title = block.splitlines()[0]
        for f in REQUIRED:
            if f'**{f}**' not in block:
                print(f"ERROR: {title} missing task schema field {f}")
                ok = False
        owner_match = re.search(r'\*\*Owner Agent\*\*:\s*([^\n]+)', block)
        if owner_match:
            owner = owner_match.group(1).strip().strip('[]')
            if owner not in ACCOUNTABLE:
                print(f"ERROR: {title} unknown owner agent {owner}")
                ok = False
    if ok:
        print(f"task board schema validation passed for {p}")
    return ok

if __name__ == '__main__':
    sys.exit(0 if validate(sys.argv[1] if len(sys.argv) > 1 else 'orchestration/tasks.md') else 1)
