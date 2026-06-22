# Installation & Activation Guide

This guide takes you from a fresh machine to an activated, governed software
factory. Target time: under 15 minutes.

## What you are installing

The DoW AI PM Builder Template is not a runnable application — it is a
**governed multi-agent workspace** you activate inside an AI coding agent
(Claude Code, Codex, or Gemini CLI). The repository carries the agent roster,
phase-gate governance, directives, and zero-dependency automation that turn a
general-purpose coding agent into a compliance-enforced software factory.

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Git | any recent | `git --version` |
| Python | 3.10+ | `python3 --version` |
| An AI coding agent | Claude Code, Codex CLI, or Gemini CLI — any one, swappable | `claude --version` / `codex --version` / `gemini --version` |
| Node.js | 18+ — only if a project instantiation includes a frontend | `node --version` |

The Python automation scripts use only the standard library. There is no
`requirements.txt` to install — by design.

**Operating systems:** macOS, Linux, and Windows. All automation entry points
are Python; on Windows use `python` (or `py`) instead of `python3` and the
same commands work in PowerShell or cmd. The `.sh` files are thin
convenience wrappers for shell users.

**AI providers:** the factory is provider-agnostic by design. `CLAUDE.md`,
`CODEX.md`, and `GEMINI.md` carry the same governance protocol for their
respective CLIs, and all process state lives in files (spec, task board,
gates, memory) — not in any provider's session. That means you can start a
project with Claude Code, hit a usage limit, and continue with Codex or
Gemini the same afternoon: the incoming agent reads its coordination file
and picks up exactly where the last one left off.

## Setup

```bash
# 1. Clone
git clone https://github.com/jdavis-cyber/dow-ai-pm-builder-template.git
cd dow-ai-pm-builder-template

# 2. Materialize the runtime agent bundle from the subagent catalog
python3 automation/install_subagents.py     # Windows: python automation\install_subagents.py

# 3. Validate the workspace
python3 automation/validate_spec.py orchestration/system_spec.md
```

`install_subagents.py` reads `subagents/install-config.json` (project profile:
languages, platforms, compliance scopes) and writes the generated runtime
manifest to `.codex/agents/runtime-manifest.json`. The manifest is a build
output — it is gitignored and regenerated per machine.

### Optional: machine-local context

If you use a local knowledge layer (e.g., the NotebookLM `nlm` CLI), create a
`CLAUDE.local.md` at the repo root with your operator-specific paths, accounts,
and notebook IDs. It is gitignored; the committed `CLAUDE.md` stays
machine-agnostic.

## Starting a New Project (the normal workflow)

**The template repo stays pristine — you never build inside it.** Each
project gets its own self-contained workspace stamped from the template:

```bash
python3 automation/init_project.py my-project            # sibling directory
python3 automation/init_project.py my-project ~/projects # or explicit parent
# Windows: python automation\init_project.py my-project C:\projects
```

This creates `my-project/` as a fresh git repository containing the pinned
factory process (agents, directives, gates), a blank spec and task board
instantiated from their templates, conventional implementation surfaces
(`src/`, `services/`, `packages/`, `database/`, `infrastructure/`, and optional
`execution/`), `docs/`, `.governance/`, and `requirements/` scaffolds, and a
`TEMPLATE_PROVENANCE.md` recording exactly which template version governs the build.

**The project folder is the deliverable.** As the factory runs, application
source accumulates in the chosen implementation surfaces, compliance evidence
in `.governance/`, decision/handoff records in `docs/decisions/` and
`docs/handoff/`, and verification/engineering artifacts in `docs/` — so at the
end you hand the customer one repository: the deployable software plus the
complete paperwork their accreditors need (RMF/ATO evidence, ADRs, test records,
gate sign-offs). The template is never part of the delivery; the provenance file
ties the process back to it.

## Activation

1. Open the **new project directory** in your AI coding agent (e.g.,
   `claude` in `my-project/`).
2. The agent's startup protocol is defined in `CLAUDE.md` (or `CODEX.md` /
   `GEMINI.md`): it must read `PROJECT.md`, `orchestration/system_spec.md`,
   and the `directives/` constitution before acting.
3. Instruct: **"Initialize the project and begin Sprint Zero."** The
   Requirements BA agent runs the discovery interview in
   `orchestration/sprint-zero-playbook.md`. Note: the blank spec
   intentionally fails `validate_spec.py` until Sprint Zero completes —
   the factory will not build against an unlocked spec.

## Verification checklist

- [ ] `python3 automation/validate_spec.py orchestration/system_spec.md` exits clean (zero-TBD spec lint)
- [ ] `.codex/agents/runtime-manifest.json` exists and lists the agent bundle
- [ ] `.agent/souls/` contains the agent SOUL definitions
- [ ] Your coding agent, on startup, reports completing the Double-Lock
      startup protocol from `CLAUDE.md`

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `validate_spec.py` fails with TBD findings | Spec is intentionally incomplete pre-Sprint-Zero | Complete Sprint Zero; the factory is fail-closed by design |
| Runtime manifest missing | Step 2 skipped | Re-run `python3 automation/install_subagents.py` |
| Agent ignores governance protocol | Agent opened outside repo root | Open the agent at the repository root so `CLAUDE.md` is auto-loaded |
| `nlm` commands fail | Optional tool not installed/authed | Install nlm CLI or remove references from your `CLAUDE.local.md` |
