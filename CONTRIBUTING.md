# Contributing

Thanks for your interest. This repository is a maintained portfolio
project demonstrating governance-as-code for AI software factories. Issues
and pull requests are welcome; the roadmap and governance model remain
maintainer-driven.

## Before you open a PR

1. Run the whole-template validation — it must pass:

   ```bash
   python3 automation/validate_template.py
   python3 automation/smoke_test_template.py
   ```

2. If you touched the roster, souls, specialization packages, or provider
   files, re-read `CLAUDE.md` §Required Validation Commands and run those too.

3. Keep the invariants intact:
   - **15 accountable agents** — the roster is mandatory; specialization
     packages are capabilities, never accountable peers.
   - **Fail-closed governance** — nothing may weaken a stop condition,
     authority boundary, or evidence obligation without an explicit
     directive change that documents why.
   - **No fabricated compliance** — framework mappings marked
     *Reference Needed* stay that way until a source clause is supplied.
   - **Provider neutrality** — `CLAUDE.md`, `CODEX.md`, and `GEMINI.md`
     carry the same operating model; keep them in sync.

4. Vendored content under `subagents/global/voltagent/` follows upstream
   (see `THIRD_PARTY_LICENSES.md`). Improvements to those packages are
   better contributed upstream first.

## Style

- Match the existing file conventions (TOML package schema, directive
  front-matter, soul structure) rather than introducing new ones.
- Documentation changes should preserve the honest-claims bar: if a document
  says something is enforced, an enforcement mechanism must exist.
