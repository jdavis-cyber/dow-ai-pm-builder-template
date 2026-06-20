# [Project Name]

**Project ID**: [PROJ-XXX]
**Status**: [Planning | Active | Complete | Archived]
**Started**: [YYYY-MM-DD]
**Completed**: [YYYY-MM-DD or In Progress]
**CPMAI Phase**: [Phase I–VI or N/A]

---

## Repository Operating Model

This repo is intended to be the authoritative project package, not only a governance sidecar. A completed or in-progress project clone should contain:

- deployable application source and runtime manifests;
- governance state, phase gates, risk, SoA, standards, and control evidence;
- decision records and architecture records;
- verification evidence and audit trail;
- handoff/continuation instructions for the next human or agent.

Keep implementation and governance separated by folder boundaries, not by separate repositories. If a project requires a different implementation layout, update `automation/gatekeeper.py` gated paths before implementation begins and record the change in `docs/decisions/`.

## Overview

[2–3 sentence description of what this project is and what problem it solves.]

## Demo

- **Live Demo**: [URL or "Not Deployed"]
- **Screenshots**: See `docs/verification/` or the project-specific design artifact path
- **Video Walkthrough**: [URL or N/A]

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | [e.g., React, Next.js, Tailwind] |
| Backend | [e.g., Node.js, Python, FastAPI] |
| Database | [e.g., PostgreSQL, MongoDB] |
| Infrastructure | [e.g., AWS, Vercel, Docker] |
| AI/ML | [e.g., OpenAI API, LangChain, local model] |

## Key Features

- [Feature 1]
- [Feature 2]
- [Feature 3]

## Governance Artifacts

This project was built using the AI PM Builder's Template governance framework. Key artifacts:

| Artifact | Status | Location |
|----------|--------|----------|
| Mission Risk Profile | [Draft/Complete/N/A] | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/` |
| Governance Scope Statement | [Draft/Complete/N/A] | `.governance/Phase_Gates/Gate1_BusinessUnderstanding/` |
| Architecture Decision Records | [Draft/Complete/N/A] | `architecture/` |
| Phase Gate Reviews | [Draft/Complete/N/A] | `.governance/Phase_Gates/` |
| Risk Register | [Draft/Complete/N/A] | `.governance/Cross_Cutting/Risk_Register/` |

## Lessons Learned

[Captured post-project. What worked, what didn't, what would you do differently.]

## Build Notes

[How to run this project locally. Setup instructions, environment variables, dependencies.]

---

*Built with the AI PM Builder's Template — Enterprise AI Governance & Lifecycle Management Framework*
*Author: Jerome Davis*
