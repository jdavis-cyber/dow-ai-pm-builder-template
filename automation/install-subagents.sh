#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${1:-$ROOT_DIR/subagents/install-config.json}"
RUNTIME_DIR="${2:-$ROOT_DIR/.codex/agents}"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "install config not found: $CONFIG_PATH" >&2
  exit 1
fi

python3 - "$ROOT_DIR" "$CONFIG_PATH" "$RUNTIME_DIR" <<'PY'
import json
import pathlib
import shutil
import sys

root = pathlib.Path(sys.argv[1])
config_path = pathlib.Path(sys.argv[2])
runtime_dir = pathlib.Path(sys.argv[3])

config = json.loads(config_path.read_text())
required_keys = [
    "version",
    "project_type",
    "languages",
    "platforms",
    "requires_accessibility",
    "requires_dod_controls",
    "requires_iso42001",
    "baseline_packages",
    "project_specific_packages",
    "regulated_packages",
]
missing = [key for key in required_keys if key not in config]
if missing:
    raise SystemExit(f"missing install-config keys: {', '.join(missing)}")

allowed_project_types = {"standard", "ai-ml", "dod-regulated", "hipaa"}
project_type = config["project_type"]
if project_type not in allowed_project_types:
    raise SystemExit(f"unsupported project_type: {project_type}")

catalog_dirs = {
    "global": root / "subagents" / "global",
    "project-specific": root / "subagents" / "project-specific",
    "dod-regulated": root / "subagents" / "dod-regulated",
}

selected = []
seen = set()
errors = []

def add_package(name: str, tier: str, reason: str) -> None:
    if name in seen:
        return
    source = catalog_dirs[tier] / f"{name}.toml"
    if not source.exists():
        errors.append(f"missing {tier} package: {source.relative_to(root)}")
        return
    seen.add(name)
    selected.append(
        {
            "name": name,
            "tier": tier,
            "reason": reason,
            "source": str(source.relative_to(root)),
        }
    )

for package in config["baseline_packages"]:
    add_package(package, "global", "baseline")

for package in config["project_specific_packages"]:
    add_package(package, "project-specific", "profile-selected")

if project_type in {"dod-regulated", "hipaa"} or config["requires_dod_controls"]:
    for package in config["regulated_packages"]:
        add_package(package, "dod-regulated", "regulated-overlay")

if errors:
    raise SystemExit("\n".join(errors))

runtime_dir.mkdir(parents=True, exist_ok=True)
for existing in runtime_dir.iterdir():
    if existing.is_file():
        existing.unlink()

for package in selected:
    source_path = root / package["source"]
    shutil.copyfile(source_path, runtime_dir / f"{package['name']}.toml")

manifest = {
    "version": config["version"],
    "project_type": project_type,
    "profile": {
        "languages": config["languages"],
        "platforms": config["platforms"],
        "requires_accessibility": config["requires_accessibility"],
        "requires_dod_controls": config["requires_dod_controls"],
        "requires_iso42001": config["requires_iso42001"],
    },
    "packages": selected,
}
(runtime_dir / "runtime-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
PY
