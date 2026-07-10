#!/usr/bin/env python3
"""Aggregate factory run-result records into objective metrics (FO-2..FO-4).

Reads docs/verification/factory-runs/*-result.json and reports run counts,
violation counts, and pass rate. The pristine template has no records; that
state reports honestly as "no runs recorded yet" and exits 0.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / 'docs/verification/factory-runs'


def collect(runs_dir=RUNS_DIR):
    records = []
    if not runs_dir.is_dir():
        return records
    for p in sorted(runs_dir.glob('*-result.json')):
        try:
            data = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError) as e:
            records.append({'file': p.name, 'parse_error': str(e)})
            continue
        data['file'] = p.name
        records.append(data)
    return records


def summarize(records):
    parse_errors = [r for r in records if 'parse_error' in r]
    results = [r for r in records if 'parse_error' not in r
               and r.get('record_type') == 'factory-run-result']
    violated = [r for r in results
                if str(r.get('outcome', '')).startswith('violation')]
    return {
        'runs_recorded': len(results),
        'runs_passed': len(results) - len(violated),
        'runs_with_violations': len(violated),
        'pass_rate': (round((len(results) - len(violated)) / len(results), 4)
                      if results else None),
        'unreadable_records': [r['file'] for r in parse_errors],
        'violation_files': [{'file': r['file'], 'outcome': r['outcome']}
                            for r in violated],
    }


def main():
    records = collect()
    summary = summarize(records)
    print(json.dumps(summary, indent=2))
    if not records:
        print('no runs recorded yet — pristine template state', file=sys.stderr)
        return 0
    if summary['unreadable_records']:
        print('ERROR: unreadable run-result records', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
