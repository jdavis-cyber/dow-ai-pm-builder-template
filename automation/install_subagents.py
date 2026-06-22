#!/usr/bin/env python3
"""Materialize the runtime agent bundle from the subagent catalog."""
import json, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
ACCOUNTABLE = ["requirements-ba","user-story-ba","ui-ux-designer","architecture-se","database-engineer","backend-developer","frontend-developer","pipeline-devops","performance-devops","qa-engineer","automation-test-engineer","scrum-master","program-analyst","documentation-se","security-compliance-officer"]
CATALOG_DIRS = {"global": ROOT/"subagents"/"global", "project-specific": ROOT/"subagents"/"project-specific", "dod-regulated": ROOT/"subagents"/"dod-regulated"}

def source_for(name):
    for tier, d in CATALOG_DIRS.items():
        p = d / f"{name}.toml"
        if p.exists():
            return tier, p
    return None, None

def git_commit():
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"

def entry(name, reason, mandatory=False):
    tier, p = source_for(name)
    if not p:
        raise SystemExit(f"missing runtime package for {name}")
    return {"name": name, "tier": tier, "reason": reason, "mandatory": bool(mandatory), "source": p.relative_to(ROOT).as_posix(), "source_soul": f".agent/souls/{name}.md"}

def main():
    config_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "subagents/install-config.json"
    runtime_dir = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / ".codex/agents"
    config = json.loads(config_path.read_text())
    if config.get("version") == 1:
        names = list(dict.fromkeys(config.get("baseline_packages", []) + config.get("project_specific_packages", []) + config.get("regulated_packages", [])))
        frameworks = {"iso_42001": "baseline" if config.get("requires_iso42001") else "not-selected"}
    else:
        names = config.get("accountable_agents", [])
        frameworks = config.get("frameworks", {})
    missing = [n for n in ACCOUNTABLE if n not in names]
    extra = [n for n in names if n not in ACCOUNTABLE]
    if missing:
        raise SystemExit("missing accountable_agents: " + ", ".join(missing))
    if extra:
        raise SystemExit("unknown accountable_agents: " + ", ".join(extra))
    accountable = [entry(n, "accountable-agent", n in config.get("mandatory_agents", []) or n == "security-compliance-officer") for n in ACCOUNTABLE]
    ownership_path = ROOT / "subagents/specialization-ownership-map.json"
    ownership = json.loads(ownership_path.read_text()) if ownership_path.exists() else {}
    specs = []
    for rel, meta in ownership.items():
        owner = meta.get("accountable_owner")
        if owner not in ACCOUNTABLE and owner != "reference-only":
            raise SystemExit(f"specialization {rel} has invalid owner {owner}")
        source = ROOT / "subagents" / rel
        if not source.exists():
            raise SystemExit(f"specialization source missing: subagents/{rel}")
        specs.append({"name": source.stem, "source": "subagents/" + rel, "accountable_owner": owner, "status": meta.get("status", "mapped"), "activation_condition": meta.get("activation_condition", "")})
    overlays = [entry(n, "regulated-overlay", False) for n in config.get("regulated_overlays", [])]
    runtime_dir.mkdir(parents=True, exist_ok=True)
    marker = runtime_dir / ".dow-runtime-dir"
    existing_entries = [p for p in runtime_dir.iterdir()]
    if existing_entries and not marker.exists():
        raise SystemExit(f"refusing to overwrite non-runtime directory without marker: {runtime_dir}")
    for existing in existing_entries:
        if existing.is_file() and existing.name != marker.name:
            existing.unlink()
    marker.write_text("managed by automation/install_subagents.py\n")
    for pkg in accountable + overlays:
        shutil.copyfile(ROOT / pkg["source"], runtime_dir / f"{pkg['name']}.toml")
    manifest = {"version": 2, "project_type": config.get("project_type", "factory-governed"), "accountable_agents": accountable, "specialization_packages": specs, "regulated_overlays": overlays, "frameworks": frameworks, "source_commit": git_commit(), "runtime_dir": str(runtime_dir)}
    (runtime_dir / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
