#!/bin/bash
# init_project.sh — Instantiate a new governed project workspace from this template.
#
# Usage:
#   bash automation/init_project.sh <project-name> [target-parent-dir]
#
# Creates <target-parent-dir>/<project-name> (default parent: the template's
# parent directory) as a SELF-CONTAINED project: fresh git repo, factory
# scaffolding copied in, blank spec/task board instantiated from their
# templates, agent runtime bundle materialized, and template provenance
# recorded. The template repo itself is never modified.
#
# The resulting folder is the deliverable: application source (execution/),
# compliance evidence (.governance/), and engineering artifacts (docs/) are
# captured there as the factory runs, and the whole repo can be handed to the
# customer for accreditation review and deployment.

set -euo pipefail

TEMPLATE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 1 ]; then
  echo "Usage: bash automation/init_project.sh <project-name> [target-parent-dir]" >&2
  exit 1
fi

PROJECT_NAME="$1"
if ! [[ "$PROJECT_NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "ERROR: project name must be lowercase kebab-case (got: $PROJECT_NAME)" >&2
  exit 1
fi

PARENT_DIR="${2:-$(dirname "$TEMPLATE_ROOT")}"
TARGET="$PARENT_DIR/$PROJECT_NAME"

if [ -e "$TARGET" ]; then
  echo "ERROR: $TARGET already exists — refusing to overwrite." >&2
  exit 1
fi

echo "▶ Instantiating project '$PROJECT_NAME' from template..."
mkdir -p "$TARGET"

# ── Factory scaffolding (copied verbatim) ───────────────────────────────────
for dir in directives subagents automation .agent memory .governance; do
  cp -R "$TEMPLATE_ROOT/$dir" "$TARGET/$dir"
done
for f in CLAUDE.md CODEX.md GEMINI.md PROJECT.md LICENSE .gitignore; do
  cp "$TEMPLATE_ROOT/$f" "$TARGET/$f"
done

# ── Orchestration: blank spec + task board from their templates ─────────────
mkdir -p "$TARGET/orchestration"
cp "$TEMPLATE_ROOT/orchestration/system-spec-template.md"  "$TARGET/orchestration/system_spec.md"
cp "$TEMPLATE_ROOT/orchestration/task-board-template.md"   "$TARGET/orchestration/tasks.md"
for f in system-spec-template.md task-board-template.md sprint-zero-playbook.md \
         escalation-template.md circuit-breaker-alert.md; do
  cp "$TEMPLATE_ROOT/orchestration/$f" "$TARGET/orchestration/$f"
done

# ── Empty work-product scaffold (filled by the factory as it runs) ──────────
mkdir -p "$TARGET/execution/backend" "$TARGET/execution/frontend" \
         "$TARGET/execution/database" "$TARGET/execution/testing" \
         "$TARGET/docs/product" "$TARGET/docs/architecture" "$TARGET/docs/verification" \
         "$TARGET/requirements"
touch "$TARGET/execution/backend/.gitkeep" "$TARGET/execution/frontend/.gitkeep" \
      "$TARGET/execution/database/.gitkeep" "$TARGET/execution/testing/.gitkeep" \
      "$TARGET/docs/product/.gitkeep" "$TARGET/docs/architecture/.gitkeep" \
      "$TARGET/docs/verification/.gitkeep" "$TARGET/requirements/.gitkeep"
cp "$TEMPLATE_ROOT/docs/architecture/adr-template.md" "$TARGET/docs/architecture/adr-template.md"

# ── Project memory starts blank ──────────────────────────────────────────────
printf '# Project Memory — %s\n\nDaily logs and agent continuity notes accumulate here.\n' \
  "$PROJECT_NAME" > "$TARGET/memory/MEMORY.md"

# ── Provenance: which factory version built this project ───────────────────
TEMPLATE_VERSION="$(git -C "$TEMPLATE_ROOT" describe --tags --always 2>/dev/null || echo unknown)"
TEMPLATE_COMMIT="$(git -C "$TEMPLATE_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
cat > "$TARGET/TEMPLATE_PROVENANCE.md" << EOF
# Template Provenance

This project workspace was instantiated from the DoW AI PM Builder Template.

| Field | Value |
|---|---|
| Template version | $TEMPLATE_VERSION |
| Template commit | $TEMPLATE_COMMIT |
| Instantiated | $(date -u +%Y-%m-%dT%H:%M:%SZ) |
| Project name | $PROJECT_NAME |

The factory process that governs this project (agent roster, directives,
phase gates) is pinned to the version above. For accreditation review of the
development process itself, refer to that template version.
EOF

# ── Fresh project README ─────────────────────────────────────────────────────
cat > "$TARGET/README.md" << EOF
# $PROJECT_NAME

A governed software project instantiated from the DoW AI PM Builder Template
(see \`TEMPLATE_PROVENANCE.md\`).

## Layout

| Path | Contents |
|---|---|
| \`execution/\` | Application source code (the deployable product) |
| \`.governance/\` | Compliance evidence: phase gates, risk registers, override register |
| \`docs/\` | Engineering artifacts: PRD, ADRs, schemas, verification records |
| \`requirements/\` | Customer-furnished requirements inputs |
| \`orchestration/\` | System spec (single source of truth) and task board |
| \`directives/\`, \`.agent/\`, \`subagents/\` | The pinned factory process governing this build |

## Getting started

1. Open this directory in your AI coding agent (Claude Code / Codex / Gemini).
2. Instruct: **"Initialize the project and begin Sprint Zero."**
3. The factory runs discovery first — no implementation until the spec is
   locked and Gate 1 clears.

## Delivery

This entire repository is the deliverable: deployable source plus the
complete evidence package needed for security accreditation review.
EOF

# ── Fresh git history ────────────────────────────────────────────────────────
git -C "$TARGET" init -q
git -C "$TARGET" add -A
git -C "$TARGET" commit -q -m "chore: instantiate $PROJECT_NAME from DoW AI PM Builder Template $TEMPLATE_VERSION"

# ── Materialize the runtime agent bundle ────────────────────────────────────
( cd "$TARGET" && bash automation/install-subagents.sh ) > /dev/null

echo "✔ Project created: $TARGET"
echo "✔ Template provenance: $TEMPLATE_VERSION ($TEMPLATE_COMMIT)"
echo "✔ Fresh git repo with initial commit; agent bundle materialized"
echo ""
echo "Next: open $TARGET in your AI coding agent and instruct:"
echo "  \"Initialize the project and begin Sprint Zero.\""
