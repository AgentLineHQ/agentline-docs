# agentline-docs

The AgentLine documentation site, built with [Mintlify](https://mintlify.com).

- **Docs site** is served by Mintlify on push to `main` once the repo is
  connected in the Mintlify dashboard.
- **API Reference** is auto-generated from `openapi.json` (the same curated
  spec the [SDKs](https://github.com/AgentLineHQ/agentline-sdks) are generated
  from), so docs, SDKs, and API always agree.

## Repo layout

```
docs.json             # Site config (navigation, theme, API settings)
openapi.json          # Curated OpenAPI spec → powers the API Reference tab
introduction.mdx      # Landing page
quickstart.mdx        # Get started
authentication.mdx    # Auth
guides/*.mdx          # Conceptual guides
sdk/*.mdx             # SDK usage (Python, Node)
AGENTS.md             # Instructions for the Mintlify AI agent + your AI tools
```

## How Mintlify works here

`docs.json` is the single source of truth for the site. It declares:

- branding (`name`, `colors.primary`, `theme`),
- a **Documentation** tab (hand-written MDX pages in `navigation.groups`),
- an **API Reference** tab declared as `{ "tab": "API Reference", "openapi": "openapi.json" }`.
  Mintlify reads `openapi.json`, groups endpoints by their OpenAPI `tags`
  (Agents, Numbers, Calls, …), and builds an interactive, try-it-now API
  reference automatically.

You do **not** hand-write the API Reference pages — they regenerate from the
spec whenever it changes.

## Run it locally

```bash
npm install -g mint      # one-time: install the Mintlify CLI
mint dev                 # live preview at http://localhost:3000
```

`mint dev` hot-reloads MDX and `docs.json`. Use it to preview before pushing.

## Quality gates

`.github/workflows/docs-check.yml` runs on every PR:

- `mint validate` — checks `docs.json` + the OpenAPI spec for errors.
- `mint broken-links` — checks every internal link resolves.

The same workflow refreshes `openapi.json` daily from the
`agentline-sdks` repo (the source of truth) and commits any change — which
triggers a docs redeploy.

## Deploy (one-time setup)

1. Go to <https://dashboard.mintlify.com> → **Add project** → connect this
   GitHub repo.
2. Set the deployment branch to `main`. Mintlify deploys on every push.
3. (Optional) Add a custom domain (e.g. `docs.agentline.cloud`) in the dashboard.

No build command is needed — Mintlify builds and hosts the site for you.

## Creating & maintaining content

### Add a page

1. Create an MDX file, e.g. `guides/billing.mdx`, with frontmatter:

   ```mdx
   ---
   title: Billing
   description: Manage your balance and view spending.
   ---

   # Billing
   ...
   ```

2. Add the file (without extension) to `docs.json` → `navigation` → the right
   group:

   ```json
   { "group": "Guides", "pages": ["guides/agents", "guides/billing"] }
   ```

3. `mint dev` to preview, then push. The PR checks validate it.

### Reorder / regroup

Edit the `navigation` arrays in `docs.json`. The sidebar follows that order.
Tabs (`navigation.tabs`) give you top-level sections; `groups` are sidebar
headers.

### Components

MDX supports Mintlify components: `<Note>`, `<Warning>`, `<Tip>`,
`<CodeGroup>`, `<Steps>`, `<Card>`, `<Accordion>`, `<Tabs>`, `<ParamField>`,
`<ResponseField>`, Mermaid diagrams, etc. See
<https://www.mintlify.com/docs/components>.

### Keep the API Reference in sync

The API Reference is never edited by hand — it comes from `openapi.json`. To
expose, hide, or rename an endpoint, change the **source of truth**: the
`SDK_SURFACE` map in
[`agentline-sdks/scripts/export_openapi.py`](https://github.com/AgentLineHQ/agentline-sdks).
The daily CI job pulls the refreshed spec into this repo, and Mintlify
regenerates the pages.

The upstream spec still includes `POST /v1/messages`. After each fetch,
`scripts/apply_agent_policy.py` stamps the production skill policy onto that
operation and the auth scheme: outbound SMS is not enabled for agents and is
not an MCP tool, keys are `al_live_...` (legacy `sk_live_...` still works),
and a US number is $2.00/month. It also states call billing ($0.10/min both
directions, 0-second calls free, one-minute minimum, then rounded up to the
cent), transcript roles `human`/`agent`, and push-context dispositions. If
`POST /v1/numbers/attach` appears in a synced spec, the script removes it.
Do not remove that step; without it the generated reference tells agents to
send SMS.

### Use the AI agent

Mintlify ships an AI agent (dashboard + `AGENTS.md`). Open the editor in the
dashboard and ask it to “add a guide on voice presets” — it drafts a PR you
review. The `AGENTS.md` in this repo gives it house-style rules.

## Branding quick changes

Edit `docs.json`:

- `name` — site/product name
- `colors.primary` — brand color (hex)
- `theme` — `mint` (or others)
- `appearance.logo` — add `images/logo.svg` and reference it
- `footer.links` — footer links
