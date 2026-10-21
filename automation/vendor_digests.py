#!/usr/bin/env python3
"""Check or refresh the SHA-256 recorded for each vendored specialization package.

The packages carry executable developer_instructions, so a change to one must be
deliberate: `check` (the default) fails on any mismatch; `update` records the
current digests after the change has been reviewed.
"""
import hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = ROOT / "subagents" / "specialization-ownership-map.json"
# Accountable-agent and regulated-overlay packages (the highest-authority
# instructions) are pinned in their own committed file.
RUNTIME_DIGESTS = ROOT / "subagents" / "runtime-package-digests.json"
RUNTIME_TIERS = ("global", "project-specific", "dod-regulated")


def runtime_packages():
    """Top-level runtime TOMLs under each tier (vendored packages are separate)."""
    out = {}
    for tier in RUNTIME_TIERS:
        for path in sorted((ROOT / "subagents" / tier).glob("*.toml")):
            out[f"{tier}/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def mismatches(ownership):
    out = []
    for rel, meta in ownership.items():
        source = ROOT / "subagents" / rel
        digest = hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
        if meta.get("sha256") != digest:
            out.append(rel)
    return out


def main(argv):
    mode = argv[0] if argv else "check"
    ownership = json.loads(MAP.read_text())
    if mode == "update":
        for rel, meta in ownership.items():
            meta["sha256"] = hashlib.sha256((ROOT / "subagents" / rel).read_bytes()).hexdigest()
        MAP.write_text(json.dumps(ownership, indent=2) + "\n")
        runtime = runtime_packages()
        RUNTIME_DIGESTS.write_text(json.dumps(runtime, indent=2) + "\n")
        print(f"recorded sha256 for {len(ownership)} specialization and {len(runtime)} runtime packages")
        return 0
    if mode != "check":
        print("usage: vendor_digests.py [check|update]")
        return 2
    bad = mismatches(ownership)
    try:
        recorded = json.loads(RUNTIME_DIGESTS.read_text())
    except (OSError, json.JSONDecodeError):
        recorded = {}
    current = runtime_packages()
    bad += sorted(rel for rel in set(recorded) | set(current) if recorded.get(rel) != current.get(rel))
    for rel in bad:
        print(f"ERROR: subagents/{rel} does not match its recorded sha256")
    if not bad:
        print(f"vendored package digests match for {len(ownership)} packages")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
