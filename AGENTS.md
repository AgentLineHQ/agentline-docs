# AGENTS.md

> House style for the Mintlify AI agent and any AI tool (Cursor, Claude Code,
> Codex) editing this docs repo.

## What this repo is

The AgentLine documentation site (Mintlify). Pages are MDX; the site is
configured by `docs.json`. The **API Reference** is auto-generated from
`openapi.json` and must **never** be edited by hand.

## Content rules

- Voice: clear, concise, developer-first. Short sentences. No marketing fluff.
- Every page starts with frontmatter `title` and `description`.
- Use H1 (`#`) once per page for the title; H2 (`##`) for sections.
- Phone numbers are always E.164, e.g. `+12125557890`.
- API keys are always `sk_live_...`. Never put a real key in examples.
- Prefer the SDK in examples (Python + Node via `<CodeGroup>`), then a `curl`
  tab when helpful. Mirror the resource/method names from the API Reference
  (e.g. `client.calls.hangup(...)`, `client.calls.hangup(...)` in Node).
- Use Mintlify components for emphasis: `<Note>`, `<Warning>`, `<Tip>`,
  `<Steps>`, `<Accordion>`. Don't overuse them.

## Editing

- To **add a page**: create the `.mdx` file AND add its path (no extension) to
  `docs.json` under the right `navigation` group. Both are required.
- To **reorder**: edit `navigation` arrays in `docs.json`.
- Never edit the `api-reference/` pages — they regenerate from `openapi.json`.
- To change what endpoints appear, edit
  `SDK_SURFACE` in the `agentline-sdks` repo, not this repo.

## Before finishing

- Run `mint dev` locally and confirm the page renders and links work.
- Ensure every new page is referenced in `docs.json`, or it won't be reachable
  in the sidebar.
- Keep code examples runnable and consistent with the SDKs
  (Python: `from agentline_ai import AgentLine`; Node:
  `import { AgentLineClient } from "agentline"`).
