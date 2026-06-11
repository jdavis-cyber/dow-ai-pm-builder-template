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
| An AI coding agent | Claude Code (recommended), Codex, or Gemini CLI | `claude --version` |
| Node.js | 18+ — only if a project instantiation includes a frontend | `node --version` |

The Python automation scripts use only the standard library. There is no
`requirements.txt` to install — by design.

## Setup

```bash
# 1. Clone
git clone https://github.com/jdavis-cyber/dow-ai-pm-builder-template.git
cd dow-ai-pm-builder-template

# 2. Materialize the runtime agent bundle from the subagent catalog
bash automation/install-subagents.sh

# 3. Validate the workspace
python3 automation/validate_spec.py orchestration/system_spec.md
```

`install-subagents.sh` reads `subagents/install-config.json` (project profile:
languages, platforms, compliance scopes) and writes the generated runtime
manifest to `.codex/agents/runtime-manifest.json`. The manifest is a build
output — it is gitignored and regenerated per machine.

### Optional: machine-local context

If you use a local knowledge layer (e.g., the NotebookLM `nlm` CLI), create a
`CLAUDE.local.md` at the repo root with your operator-specific paths, accounts,
and notebook IDs. It is gitignored; the committed `CLAUDE.md` stays
machine-agnostic.

## Activation

1. Open the repository root in your AI coding agent (e.g., `claude` in this
   directory).
2. The agent's startup protocol is defined in `CLAUDE.md` (or `CODEX.md` /
   `GEMINI.md`): it must read `PROJECT.md`, `orchestration/system_spec.md`,
   and the `directives/` constitution before acting.
3. To start a new project, instruct: **"Initialize the project and begin
   Sprint Zero."** The Requirements BA agent runs the discovery interview in
   `orchestration/sprint-zero-playbook.md`.

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
| Runtime manifest missing | Step 2 skipped | Re-run `bash automation/install-subagents.sh` |
| Agent ignores governance protocol | Agent opened outside repo root | Open the agent at the repository root so `CLAUDE.md` is auto-loaded |
| `nlm` commands fail | Optional tool not installed/authed | Install nlm CLI or remove references from your `CLAUDE.local.md` |
