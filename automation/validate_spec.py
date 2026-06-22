#!/usr/bin/env python3
import argparse, pathlib, re, sys
PLACEHOLDER_RE = re.compile(r'(?<![!])\[[^\]]+\](?!\()')
REQUIRED_TEMPLATE_FIELDS = ['Project Name','Status','System Overview','Architecture Specification','Agent Work Packages']
GAP_LABELS = ['Draft','Gap','Reference Needed','Not Authoritatively Mapped','Pending','N/A','Not Approved']

def validate(path, mode):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"ERROR: Spec file not found: {p}")
        return False
    txt = p.read_text(encoding='utf-8')
    errors = []
    if mode == 'template':
        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in txt:
                errors.append(f"template integrity missing required field: {field}")
        if not PLACEHOLDER_RE.search(txt):
            errors.append('template integrity requires explicit placeholders')
    elif mode == 'draft':
        if not any(label in txt for label in GAP_LABELS):
            errors.append('draft completeness: unresolved values require an explicit Draft/Gap/Pending/Not Approved status label')
        for i, line in enumerate(txt.splitlines(), 1):
            if ('TBD' in line or 'TODO' in line) and not any(label in line for label in GAP_LABELS):
                errors.append(f"draft completeness line {i}: TBD/TODO requires explicit gap/status label")
    elif mode == 'locked':
        for i, line in enumerate(txt.splitlines(), 1):
            if PLACEHOLDER_RE.search(line) or 'TBD' in line or 'TODO' in line:
                errors.append(f"lock readiness line {i}: unresolved placeholder/TBD/TODO")
            if any(label in line for label in ['Reference Needed','Not Authoritatively Mapped','Pending']):
                errors.append(f"lock readiness line {i}: unresolved gap label remains")
    if errors:
        print(f"--- SPEC VALIDATION FAILED ({mode}) for {p} ---")
        print('\n'.join(errors))
        return False
    print(f"+++ SPEC VALIDATION PASSED ({mode}) for {p} +++")
    return True

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['template','draft','locked'], default='locked')
    ap.add_argument('spec')
    ns = ap.parse_args()
    sys.exit(0 if validate(ns.spec, ns.mode) else 1)
