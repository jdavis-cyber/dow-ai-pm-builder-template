#!/usr/bin/env python3
import argparse, pathlib, re, sys
PLACEHOLDER_RE = re.compile(r'(?<![!])\[[^\]]+\](?!\()')
REQUIRED_TEMPLATE_FIELDS = ['Project Name','Status','System Overview','Architecture Specification','Agent Work Packages']
GAP_LABELS = ['Draft','Gap','Reference Needed','Not Authoritatively Mapped','Pending','N/A','Not Approved']
# Where a status label sits: the start of a line, list item, field value,
# table cell, bracket or slash-separated choice (optionally in bold).
LABEL_START = r'(?:^|[:|(\[/])\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*'
# What may follow a label that stands alone as the whole value.
BARE_END = r'(?:\*\*|__)?\s*(?:$|[|)\]/.,;])'
# Explicit unresolved labels, not ordinary prose such as "air gap", "gap
# analysis", "the drafting team" or "N/A because the system has no UI".
UNRESOLVED_LABEL_RES = [
    # "Gap" followed by a separator or closing bracket, in any case.
    re.compile(r'(?<!\w)(?<!air )gap(?:\s*[:—–-]|\s*\]|\s*\)|\s*$)', re.IGNORECASE),
    # A value that starts with "Gap" ("Gap owner unknown"), other than gap analysis/assessment.
    re.compile(LABEL_START + r'gap\b(?!\s+(?:analysis|analyses|assessment)\b)', re.IGNORECASE),
    # "Draft" in a label position, or a whole value that is just "draft".
    re.compile(LABEL_START + r'Draft\b'),
    re.compile(LABEL_START + r'draft' + BARE_END, re.IGNORECASE),
    re.compile(r'\bNot Approved\b'),
    re.compile(LABEL_START + r'not approved\b', re.IGNORECASE),
    # "N/A" left as the whole answer. "N/A — reason" or "N/A because ..." is resolved.
    re.compile(r'(?<![\w/])N/A' + BARE_END, re.IGNORECASE),
    re.compile(r'Reference Needed|Not Authoritatively Mapped|Pending'),
]


def unresolved_label(line):
    """True when the line still carries an unresolved status label."""
    return any(rx.search(line) for rx in UNRESOLVED_LABEL_RES)


def locked_problems(txt):
    """Lock readiness problems in a spec's text; empty when it can be locked."""
    errors = []
    for i, line in enumerate(txt.splitlines(), 1):
        if PLACEHOLDER_RE.search(line) or 'TBD' in line or 'TODO' in line:
            errors.append(f"lock readiness line {i}: unresolved placeholder/TBD/TODO")
        if unresolved_label(line):
            errors.append(f"lock readiness line {i}: unresolved status label remains")
    return errors

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
        errors.extend(locked_problems(txt))
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
