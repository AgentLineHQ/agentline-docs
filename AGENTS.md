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
- API keys are always `al_live_...` (legacy `sk_live_...` still works). Never put a real key in examples.
- Phone numbers are **US only** and cost **$2.00/month per number**. Calls are **$0.10/min** in both directions: 0-second calls are free, connected calls have a one-minute minimum, then the actual duration rounded up to the cent. Do not document Canada, a one-time number fee, `$0.08/min`, or `$0.02/msg`.
- Push context (`POST /v1/calls/{id}/context`) sends short facts plus `disposition` (`progress`, `done`, `facts`, `failed`, `noop`). It is not spoken verbatim.
- Transcript roles are `human` and `agent`. A `call.utterance` `conversation` uses `user` and `assistant`.
- Do not document `POST /v1/numbers/attach`. It is operator-only.
- **Outbound SMS is not enabled for agents.** Document inbound SMS and message listing only. `POST /v1/messages` may remain in the generated API reference; say it is not enabled and is not an MCP tool. Do not list `send_sms` or `send_message` as MCP tools.
- MCP is `https://api.agentline.cloud/mcp` via `mcp-remote` and a Bearer key.
- Voice presets are `female-1`, `female-2`, `female-3`, `male-1`, `male-2`, and `male-3`.
- Prefer the Python SDK in examples (`from agentline_ai import AgentLine`), then a
  `curl` or `fetch` tab. The Node package is not on npm. Do not document
  `npm i agentline` as an install that works. Live transfers dial only
  `owner_phone`; a different `transfer_number` is rejected.
- Use Mintlify components for emphasis: `<Note>`, `<Warning>`, `<Tip>`,
  `<Steps>`, `<Accordion>`. Don't overuse them.

## Editing

- To **add a page**: create the `.mdx` file AND add its path (no extension) to
  `docs.json` under the right `navigation` group. Both are required.
- To **reorder**: edit `navigation` arrays in `docs.json`.
- Never edit the `api-reference/` pages â€” they regenerate from `openapi.json`.
- To change what endpoints appear, edit
  `SDK_SURFACE` in the `agentline-sdks` repo, not this repo.

## Before finishing

- Run `mint dev` locally and confirm the page renders and links work.
- Ensure every new page is referenced in `docs.json`, or it won't be reachable
  in the sidebar.
- Keep Python examples runnable: `from agentline_ai import AgentLine`.
  Node examples use `fetch` against `https://api.agentline.cloud` with
  `Authorization: Bearer al_live_...` until the package is published.
  `scripts/apply_agent_policy.py` restores those `fetch` tabs if a sync puts
  the unpublished `client.*` SDK back.
