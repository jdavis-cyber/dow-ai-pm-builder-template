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

## Choose the Model per Session

No agent package pins a model or a reasoning effort. Whoever runs the factory
picks them in the adapter command, so a session can move up or down as models
and prices change, for example:

```bash
FACTORY_ADAPTER=shell FACTORY_ADAPTER_COMMAND='codex exec --stdin -m <model> -c model_reasoning_effort=<low|medium|high>' ./automation/factory.sh
```

With no flags the runtime CLI uses its own configured default. Set
`FACTORY_MODEL_ID` to the same model name if you want run results to record it.

## Instantiate a Project

```bash
python3 automation/init_project.py my-project /path/to/parent
```

For conversational startup, the canonical operator phrase is documented in `KICKOFF.md`:

```text
Start a new project from the DoW AI PM Builder Template and begin Sprint Zero.
```

The interview process owns discovery details; operators should not need to supply mission, objectives, inputs, files, links, or governance caveats in the initial phrase.

Then open the generated project with Claude Code, Codex, Gemini, or another provider. Provider coordination files carry the same governance protocol.

## Task Runner

```bash
python3 automation/validate_tasks.py orchestration/tasks.md
python3 automation/run_factory.py
```

The runner generates scoped prompts and refuses tasks with incomplete dependencies or missing gate evidence. It does not mark work done by itself.
