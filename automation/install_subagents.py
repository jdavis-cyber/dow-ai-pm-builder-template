#!/usr/bin/env python3
"""Materialize the runtime agent bundle from the subagent catalog.

Cross-platform (macOS / Linux / Windows), stdlib only.

Usage:
    python3 automation/install_subagents.py [config_path] [runtime_dir]

Defaults: subagents/install-config.json -> .codex/agents/
(install-subagents.sh remains as a thin wrapper for shell users.)
"""

import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> None:
    config_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "subagents" / "install-config.json"
    runtime_dir = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / ".codex" / "agents"

    if not config_path.is_file():
        raise SystemExit(f"install config not found: {config_path}")

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
        "global": ROOT / "subagents" / "global",
        "project-specific": ROOT / "subagents" / "project-specific",
        "dod-regulated": ROOT / "subagents" / "dod-regulated",
    }

    selected = []
    seen = set()
    errors = []

    def add_package(name: str, tier: str, reason: str) -> None:
        if name in seen:
            return
        source = catalog_dirs[tier] / f"{name}.toml"
        if not source.exists():
            errors.append(f"missing {tier} package: {source.relative_to(ROOT)}")
            return
        seen.add(name)
        selected.append(
            {
                "name": name,
                "tier": tier,
                "reason": reason,
                "source": source.relative_to(ROOT).as_posix(),
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
        source_path = ROOT / package["source"]
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


if __name__ == "__main__":
    main()
