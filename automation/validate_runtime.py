#!/usr/bin/env python3
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCOUNTABLE = ["requirements-ba","user-story-ba","ui-ux-designer","architecture-se","database-engineer","backend-developer","frontend-developer","pipeline-devops","performance-devops","qa-engineer","automation-test-engineer","scrum-master","program-analyst","documentation-se","security-compliance-officer"]

def validate(path):
    path = pathlib.Path(path)
    m = json.loads(path.read_text())
    ok = True
    def err(msg):
        nonlocal ok
        print(f"ERROR: {msg}")
        ok = False
    agents = m.get('accountable_agents', [])
    names = [a.get('name') if isinstance(a, dict) else a for a in agents]
    if names != ACCOUNTABLE:
        err(f"accountable_agents mismatch: {names}")
    if len(names) != 15:
        err(f"expected 15 accountable agents, found {len(names)}")
    for a in agents:
        if not isinstance(a, dict):
            err('accountable agent entries must be objects')
            continue
        src = ROOT / a.get('source', '')
        soul = ROOT / a.get('source_soul', f".agent/souls/{a.get('name')}.md")
        if not src.exists():
            err(f"runtime source missing: {a.get('source')}")
        if not soul.exists():
            err(f"SOUL missing: {soul}")
        if not (path.parent / f"{a.get('name')}.toml").exists():
            err(f"materialized TOML missing: {a.get('name')}.toml")
    sec = next((a for a in agents if isinstance(a, dict) and a.get('name') == 'security-compliance-officer'), None)
    if not sec or not sec.get('mandatory'):
        err('Security & Compliance Officer is not marked mandatory')
    specs = m.get('specialization_packages', [])
    sources = [s.get('source') for s in specs]
    if len(specs) != 136:
        err(f"expected 136 specialization packages, found {len(specs)}")
    if len(set(sources)) != len(sources):
        err('duplicate specialization package sources in manifest')
    for s in specs:
        owner = s.get('accountable_owner')
        if owner not in ACCOUNTABLE and owner != 'reference-only':
            err(f"specialization {s.get('source')} invalid owner {owner}")
        source = ROOT / s.get('source', '')
        if not source.exists():
            err(f"specialization source missing: {s.get('source')}")
    if ok:
        print('runtime validation passed: 15 accountable agents, mandatory security, 136 specialization packages valid')
    return ok

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.codex/agents/runtime-manifest.json'
    sys.exit(0 if validate(target) else 1)
