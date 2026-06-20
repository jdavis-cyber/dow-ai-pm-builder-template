#!/usr/bin/env python3
"""Instantiate a new governed project workspace from this template.

Cross-platform (macOS / Linux / Windows), stdlib only.

Usage:
    python3 automation/init_project.py <project-name> [target-parent-dir]

Creates <target-parent-dir>/<project-name> (default parent: the template's
parent directory) as a SELF-CONTAINED project: fresh git repo, factory
scaffolding copied in, blank spec/task board instantiated from their
templates, agent runtime bundle materialized, and template provenance
recorded. The template repo itself is never modified.

The resulting folder is the deliverable: application source (typically src/,
services/, packages/, database/, and infrastructure/), compliance evidence
(.governance/), decisions, verification evidence, and engineering artifacts
(docs/) are captured there as the factory runs, and the whole repo can be
handed to the customer for accreditation review and deployment.
"""

import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

SCAFFOLD_DIRS = ["directives", "subagents", "automation", ".agent", "memory", ".governance"]
SCAFFOLD_FILES = ["CLAUDE.md", "CODEX.md", "GEMINI.md", "PROJECT.md", "LICENSE", ".gitignore"]
ORCHESTRATION_FILES = [
    "system-spec-template.md",
    "task-board-template.md",
    "sprint-zero-playbook.md",
    "escalation-template.md",
    "circuit-breaker-alert.md",
]
WORK_SCAFFOLD = [
    "src",
    "services",
    "packages",
    "database",
    "infrastructure",
    "execution",
    "docs/product",
    "docs/architecture",
    "docs/decisions",
    "docs/handoff",
    "docs/verification",
    "requirements",
]


def git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 automation/init_project.py <project-name> [target-parent-dir]")

    project_name = sys.argv[1]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", project_name):
        raise SystemExit(f"ERROR: project name must be lowercase kebab-case (got: {project_name})")

    parent_dir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else TEMPLATE_ROOT.parent
    target = parent_dir / project_name
    if target.exists():
        raise SystemExit(f"ERROR: {target} already exists — refusing to overwrite.")

    print(f"▶ Instantiating project '{project_name}' from template...")
    target.mkdir(parents=True)

    # ── Factory scaffolding (copied verbatim) ──────────────────────────────
    for d in SCAFFOLD_DIRS:
        shutil.copytree(TEMPLATE_ROOT / d, target / d)
    for f in SCAFFOLD_FILES:
        shutil.copyfile(TEMPLATE_ROOT / f, target / f)

    # ── Orchestration: blank spec + task board from their templates ────────
    orch = target / "orchestration"
    orch.mkdir()
    shutil.copyfile(TEMPLATE_ROOT / "orchestration" / "system-spec-template.md", orch / "system_spec.md")
    shutil.copyfile(TEMPLATE_ROOT / "orchestration" / "task-board-template.md", orch / "tasks.md")
    for f in ORCHESTRATION_FILES:
        shutil.copyfile(TEMPLATE_ROOT / "orchestration" / f, orch / f)

    # ── Empty work-product scaffold (filled by the factory as it runs) ─────
    for d in WORK_SCAFFOLD:
        (target / d).mkdir(parents=True, exist_ok=True)
        (target / d / ".gitkeep").touch()
    shutil.copyfile(
        TEMPLATE_ROOT / "docs" / "architecture" / "adr-template.md",
        target / "docs" / "architecture" / "adr-template.md",
    )
    for rel in [
        "docs/decisions/ADR-000-template.md",
        "docs/handoff/documentation-map.md",
        "docs/handoff/project-continuation-guide.md",
        "docs/handoff/project-instantiation-checklist.md",
        "docs/handoff/repo-controls-checklist.md",
        "docs/templates/artifact-status-block.md",
        "docs/verification/evidence-index.md",
    ]:
        src = TEMPLATE_ROOT / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    # ── Project memory starts blank ─────────────────────────────────────────
    (target / "memory" / "MEMORY.md").write_text(
        f"# Project Memory — {project_name}\n\n"
        "Daily logs and agent continuity notes accumulate here.\n"
    )

    # ── Provenance: which factory version built this project ───────────────
    try:
        template_version = git(["describe", "--tags", "--always"], TEMPLATE_ROOT)
        template_commit = git(["rev-parse", "HEAD"], TEMPLATE_ROOT)
    except SystemExit:
        template_version = template_commit = "unknown"
    instantiated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (target / "TEMPLATE_PROVENANCE.md").write_text(
        "# Template Provenance\n\n"
        "This project workspace was instantiated from the DoW AI PM Builder Template.\n\n"
        "| Field | Value |\n|---|---|\n"
        f"| Template version | {template_version} |\n"
        f"| Template commit | {template_commit} |\n"
        f"| Instantiated | {instantiated} |\n"
        f"| Project name | {project_name} |\n\n"
        "The factory process that governs this project (agent roster, directives,\n"
        "phase gates) is pinned to the version above. For accreditation review of the\n"
        "development process itself, refer to that template version.\n"
    )

    # ── Fresh project README ────────────────────────────────────────────────
    (target / "README.md").write_text(
        f"# {project_name}\n\n"
        "A governed software project instantiated from the DoW AI PM Builder Template\n"
        "(see `TEMPLATE_PROVENANCE.md`).\n\n"
        "## Layout\n\n"
        "| Path | Contents |\n|---|---|\n"
        "| `src/`, `services/`, `packages/` | Conventional application source locations; use the structure your stack needs |\n"
        "| `database/`, `infrastructure/` | Data and deployment/runtime infrastructure artifacts |\n"
        "| `execution/` | Optional/legacy implementation workspace; still gate-protected |\n"
        "| `.governance/` | Compliance evidence: phase gates, risk registers, override register |\n"
        "| `docs/decisions/` | ADRs and governance decision records |\n"
        "| `docs/handoff/` | Continuation and reviewer navigation package |\n"
        "| `docs/verification/` | Append-only verification and evidence records |\n"
        "| `docs/product/`, `docs/architecture/` | PRD, user stories, architecture, schemas, and related artifacts |\n"
        "| `requirements/` | Customer-furnished requirements inputs |\n"
        "| `orchestration/` | System spec (single source of truth) and task board |\n"
        "| `directives/`, `.agent/`, `subagents/` | The pinned factory process governing this build |\n\n"
        "## Getting started\n\n"
        "1. Open this directory in your AI coding agent — **Claude Code, Codex, or\n"
        "   Gemini CLI all work**; the matching coordination file (`CLAUDE.md`,\n"
        "   `CODEX.md`, `GEMINI.md`) carries the same governance protocol, so you can\n"
        "   switch providers mid-project without losing process state.\n"
        '2. Instruct: **"Initialize the project and begin Sprint Zero."**\n'
        "3. The factory runs discovery first — no implementation until the spec is\n"
        "   locked and Gate 1 clears.\n\n"
        "## Delivery\n\n"
        "This entire repository is the deliverable: deployable source plus the\n"
        "complete evidence package needed for security accreditation review.\n"
    )

    # ── Fresh git history ───────────────────────────────────────────────────
    git(["init", "-q"], target)
    git(["add", "-A"], target)
    git(["commit", "-q", "-m",
         f"chore: instantiate {project_name} from DoW AI PM Builder Template {template_version}"], target)

    # ── Materialize the runtime agent bundle ───────────────────────────────
    subprocess.run(
        [sys.executable, str(target / "automation" / "install_subagents.py"),
         str(target / "subagents" / "install-config.json"),
         str(target / ".codex" / "agents")],
        check=True, capture_output=True,
    )

    print(f"✔ Project created: {target}")
    print(f"✔ Template provenance: {template_version} ({template_commit})")
    print("✔ Fresh git repo with initial commit; agent bundle materialized")
    print()
    print(f"Next: open {target} in your AI coding agent (Claude Code, Codex, or Gemini)")
    print('  and instruct: "Initialize the project and begin Sprint Zero."')


if __name__ == "__main__":
    main()
