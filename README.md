# DoW AI PM Builder Template

**Bring AI into the way your team delivers.**

AI can help a team turn a customer need into working software. The work still needs a shared direction, clear responsibilities and a sound basis for deciding when it is ready.

DoW provides a reusable foundation for that delivery process. Discovery, task definitions, AI assistance, verification and decision records live together in the project repository. Governance becomes part of doing the work: defining it, handing it off, checking it and deciding what comes next.

[Explore the delivery model](KICKOFF.md) · [Try the template](INSTALL.md) · [Inspect the implementation](automation/governed_factory.py)

## From customer need to coordinated work

**Define the outcome.** Sprint Zero prompts help a team establish the problem, intended users, constraints and acceptance criteria before implementation starts. The system specification gives that work a common reference.

**Make each task actionable.** Task records name an accountable role, required inputs, dependencies, acceptance criteria, verification method and handoff target. The role packages supply instructions for AI-assisted work across requirements, design, engineering, security and verification.

**Carry the evidence forward.** Handoff records capture outputs, verification performed and unresolved gaps. Decision templates give reviewers a place to assess readiness, record conditions and explain a go/no-go recommendation.

The aim is a delivery record that a developer can act on, a reviewer can inspect and a program lead can use to make an informed decision.

## Potential uses

Suppose a customer needs a feature that shows the status of a service request. A team could use the template to define the user need, divide the feature into owned tasks, use AI to assist with implementation, and carry test evidence and open issues into review.

The feature, the reasons behind it and the conditions for accepting it would share a project structure.

## How the engineering supports the process

Generated projects start **Draft / Not Approved**. The dispatcher selects one eligible task against dependencies and recorded authority. Assisted mode prints its task packet; a configured shell adapter can pass that work to the team's chosen runtime.

After a successful shell-adapter return, checks examine task status, referenced evidence and certain unauthorized file changes. The repository also includes validators, regression tests and a smoke test for project generation.

The 15 role packages define responsibilities and instructions; the runner does not launch 15 independent agents. Teams retain responsibility for approvals, evidence quality and release decisions.

## Explore or try it

- **Understand the workflow:** [Sprint Zero](orchestration/sprint-zero-playbook.md), [task schema](orchestration/task-schema.md) and [handoff record](directives/templates/agent-handoff-record.md).
- **Evaluate locally:** follow [INSTALL.md](INSTALL.md) for setup and validation commands, then generate a project in an unused directory. Generation writes files and creates an initial Git commit.
- **Choose how AI participates:** begin with assisted task packets; review the [adapter configuration](factory.config.example.json) before connecting a model runtime.
- **Explore optional assurance references:** [control matrix](docs/governance-frameworks/factory-control-matrix.md), [risk register](docs/governance-frameworks/factory-risk-register.md) and [go/no-go template](directives/templates/go-no-go-recommendation.md).

## Evaluation boundaries

DoW is an evaluation template for adapting AI-assisted delivery to a team's environment. Shell adapters run with the operator's permissions. Validation checks aid human review; they do not replace security controls, judgment about evidence quality or deployment decisions. Framework mappings do not confer certification or impose routine repository paperwork; see the [maintenance scope](docs/governance-frameworks/repository-maintenance.md). See [SECURITY.md](SECURITY.md) and the [control matrix](docs/governance-frameworks/factory-control-matrix.md) for scope, mechanisms and limitations.

Built by [Jerome Davis / Second Order Strategy](https://secondorderstrategy.com). [Contribute](CONTRIBUTING.md) · [MIT license](LICENSE) · [VoltAgent attribution](THIRD_PARTY_LICENSES.md).
