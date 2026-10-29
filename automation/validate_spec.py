#!/usr/bin/env python3
import argparse, pathlib, re, sys
PLACEHOLDER_RE = re.compile(r'(?<![!])\[[^\]]+\](?!\()')
REQUIRED_TEMPLATE_FIELDS = ['Project Name','Status','System Overview','Architecture Specification','Agent Work Packages']
GAP_LABELS = ['Draft','Gap','Reference Needed','Not Authoritatively Mapped','Pending','N/A','Not Approved']
# Where a status label sits: the start of a line, list item, field value,
# table cell, bracket or slash-separated choice (optionally in bold).
LABEL_START = r'(?:^|[:|(\[/])\s*(?:[-*+]\s+)?(?:\*\*|__)?\s*'
# What may follow a label that is the whole value: the end of the line or of
# the cell, a closing bracket, another slash choice, or trailing punctuation.
BARE_END = r'(?:\*\*|__)?\s*(?:$|[|)\]/.,;])'
# What may follow a status label that carries a qualifier rather than prose:
# a separator and a reason ("Draft — awaiting review"), a version ("Draft
# v0.3") or a date ("Draft (2026-10-01)").
QUALIFIED_END = (r'(?:\*\*|__)?\s*(?:[:—–]|\s-\s|v\d+(?:\.\d+)*\b|\d+\.\d+(?:\.\d+)*\b|\(?\s*\d{4}-\d{2}-\d{2})')


def _status_label(words):
    """A label that counts only as the whole value or with a qualifier, never as
    the first word of a sentence ("Draft user stories from ...")."""
    return re.compile(LABEL_START + words + r'(?=' + BARE_END + '|' + QUALIFIED_END + ')', re.IGNORECASE)


# Words that keep "Gap <noun> ..." a placeholder ("Gap owner unknown").
GAP_UNRESOLVED_WORDS = r'(?:unknown|outstanding|open|unresolved|pending|missing|tbd|needed|undecided|unassigned)'
# Explicit unresolved labels, not ordinary prose such as "air gap", "gap
# analysis", "Draft user stories", "the drafting team" or "N/A because the
# system has no UI".
UNRESOLVED_LABEL_RES = [
    # "Gap" followed by a separator or closing bracket, in any case.
    re.compile(r'(?<!\w)(?<!air )gap(?:\s*[:—–-]|\s*\]|\s*\)|\s*$)', re.IGNORECASE),
    # A value that starts with "Gap" and says the gap is still open ("Gap owner unknown").
    re.compile(LABEL_START + r'gap\b(?:\s+\w+){0,3}?\s+' + GAP_UNRESOLVED_WORDS + r'\b', re.IGNORECASE),
    _status_label(r'draft'),
    _status_label(r'not\s+approved'),
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
    # Survive a console that is not UTF-8, e.g. cp1252 on Windows (AI-1151).
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    sys.dont_write_bytecode = True  # leave no __pycache__ behind in the project
    import safe_console
    safe_console.make_console_safe()
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['template','draft','locked'], default='locked')
    ap.add_argument('spec')
    ns = ap.parse_args()
    sys.exit(0 if validate(ns.spec, ns.mode) else 1)
