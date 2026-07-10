# Third-party licenses

This repository vendors and derives content from the following third-party
projects. The attribution and license text below must be preserved in all
copies or substantial portions of that content (MIT license condition).

## VoltAgent subagent collections

- **What is vendored:** the 136 specialization/capability packages under
  `subagents/global/voltagent/` (10 domain directories), adapted from the
  upstream collections for use inside this template's governance model.
- **What is derived:** the 20 execution-depth wrapper packages at
  `subagents/global/*.toml` whose headers cite an upstream
  `Source:` — VoltAgent-derived content with governance metadata
  (accountable owner, source soul, evidence obligations) added by this
  repository.
- **Upstreams:**
  - <https://github.com/VoltAgent/awesome-claude-code-subagents> — MIT,
    Copyright (c) 2025 VoltAgent
  - <https://github.com/VoltAgent/awesome-codex-subagents> — MIT,
    Copyright (c) 2026 VoltAgent
- **Not vendored:** everything else in this repository — including
  `.agent/souls/`, the 14 root-level accountable-agent identity packages in
  `subagents/global/*.toml` (generated from this repo's own souls, no
  upstream `Source:` header), `subagents/dod-regulated/`, `automation/`,
  and `directives/` — is original work under this repository's own LICENSE.

### Upstream license text (MIT)

```text
MIT License

Copyright (c) 2025 VoltAgent (awesome-claude-code-subagents)
Copyright (c) 2026 VoltAgent (awesome-codex-subagents)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
