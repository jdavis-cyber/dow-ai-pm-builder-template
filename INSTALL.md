# Installation and Activation

## Requirements

- Python 3.9+ standard library
- Git
- Optional: pytest for `python3 -m pytest`; otherwise use `python3 -m unittest discover -s tests`.

## Validate the Template

```bash
python3 automation/validate_template.py
python3 automation/smoke_test_template.py
python3 -m unittest discover -s tests
```

## Materialize Runtime Agents

```bash
python3 automation/install_subagents.py subagents/install-config.json .codex/agents
python3 automation/validate_runtime.py .codex/agents/runtime-manifest.json
```

The runtime manifest must contain all 15 accountable agents and mark Security & Compliance Officer mandatory.

## Instantiate a Project

```bash
python3 automation/init_project.py my-project /path/to/parent
```

Then open the generated project with Claude Code, Codex, Gemini, or another provider. Provider coordination files carry the same governance protocol.

## Task Runner

```bash
python3 automation/validate_tasks.py orchestration/tasks.md
python3 automation/run_factory.py
```

The runner generates scoped prompts and refuses tasks with incomplete dependencies or missing gate evidence. It does not mark work done by itself.
