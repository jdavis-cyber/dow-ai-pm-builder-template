# DoW AI PM Builder Template

A provider-agnostic, single-repository template for instantiating a governed AI software factory.

## Operating Model

The template creates a complete project package: application source, governance records, decision logic, verification evidence, handoff materials, agent identities, runtime packages, and orchestration logic live together with clear folder boundaries.

## Factory Team

- **15 accountable agents** are permanent and mandatory in the factory handoff model.
- **Security & Compliance Officer is always installed** and participates in every phase gate.
- **136 specialization packages** under `subagents/global/voltagent/` are capability packages/tools mapped to accountable owners in `subagents/specialization-ownership-map.json`.

See `.agent/AGENT-ROSTER.md` and `subagents/SPECIALIZATION-LIBRARY.md`.

## Framework Applicability

| Framework | Treatment |
|---|---|
| CPMAI | Baseline lifecycle backbone for the factory |
| ISO/IEC 42001 | Baseline AIMS management-system target for factory behavior |
| NIST AI RMF | Baseline risk-function overlay |
| ISO/IEC 27001 | Crosswalk candidate when source clauses are supplied/confirmed |
| ISO/IEC 27701 | Reference Needed — Not Authoritatively Mapped |
| CMMC / FedRAMP / HIPAA / SOC 2 | Conditional product overlays only |

Do not infer product compliance or fabricate mappings.

## Fresh Clone Validation

```bash
python3 automation/validate_template.py
python3 automation/smoke_test_template.py
```

## Instantiate a Project

```bash
python3 automation/init_project.py my-project /tmp
cd /tmp/my-project
python3 automation/validate_runtime.py .codex/agents/runtime-manifest.json
```

For agent/operator kickoff, use the canonical phrase in `KICKOFF.md`:

```text
Start a new project from the DoW AI PM Builder Template.
```

The factory should ask only for the minimum missing workspace detail, then let the Sprint Zero / Phase 0 interview collect mission, objectives, inputs, links, constraints, and authority boundaries.

Generated projects begin in Draft / Not Approved status. Sprint Zero discovery and phase gates must populate evidence before implementation proceeds.

## Runtime Output

`.codex/agents/` is generated runtime output from `automation/install_subagents.py` and is ignored by git by default. The source of truth remains `subagents/` plus `.agent/souls/`.
