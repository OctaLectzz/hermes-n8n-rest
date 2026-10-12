# Hermes n8n REST

A complementary REST API integration for Hermes Agent and n8n. Keep the official
`n8n-official` MCP server enabled as the primary workflow integration; use this
plugin when REST endpoints are useful as a secondary path.

## Tools

- `n8n_rest_list_workflows` — list workflows with pagination.
- `n8n_rest_get_workflow` — fetch one workflow by ID.
- `n8n_rest_create_workflow` — create a workflow without activating it.
- `n8n_rest_update_workflow` — update a workflow by ID.
- `n8n_rest_set_workflow_active` — activate or deactivate a workflow.

Create/update/activation tools change server state. Review workflow JSON and
confirm the intended target before invoking them. Activation may start production
triggers. Use a dedicated n8n API key with the minimum permissions available.

## Configuration

Set these in the Hermes container environment (not in this repository):

- `N8N_BASE_URL=https://n8n.example.com`
- `N8N_API_KEY=<your n8n API key>`

The plugin refuses non-HTTPS remote URLs. Plain HTTP is permitted only for
localhost testing. Never commit API keys, paste them into prompts, or place them
in workflow JSON.

## Offline tests

The tests use only Python's standard library and do not contact n8n:

```sh
python -m unittest discover -s tests -v
```

## Install

Install from the Hermes Plugins dashboard using this repository URL after the
source has been reviewed and validated. Do not enable the plugin until tests
and a controlled read-only connection test pass. The existing MCP configuration
is not changed by this plugin.
