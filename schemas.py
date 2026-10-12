"""JSON schemas exposed to the Hermes tool registry."""

ALL_SCHEMAS = [
    {
        "name": "n8n_rest_list_workflows",
        "description": "List n8n workflows through the REST API. Use MCP n8n-official as the primary path when available.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum workflows to return (1-100)."},
                "cursor": {"type": "string", "description": "Optional pagination cursor returned by n8n."},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "n8n_rest_get_workflow",
        "description": "Get one n8n workflow by ID using the REST API.",
        "parameters": {
            "type": "object",
            "properties": {"workflow_id": {"type": "string", "minLength": 1, "description": "Workflow ID."}},
            "required": ["workflow_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "n8n_rest_create_workflow",
        "description": "Create an n8n workflow from a workflow JSON object. This creates a workflow but does not activate it.",
        "parameters": {
            "type": "object",
            "properties": {"workflow": {"type": "object", "description": "n8n workflow object containing at least name, nodes, and connections."}},
            "required": ["workflow"],
            "additionalProperties": False,
        },
    },
    {
        "name": "n8n_rest_update_workflow",
        "description": "Update an existing n8n workflow by ID using a complete workflow object. Confirm the intended changes before calling.",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "minLength": 1, "description": "Workflow ID to update."},
                "workflow": {"type": "object", "description": "Workflow fields to send to n8n."},
            },
            "required": ["workflow_id", "workflow"],
            "additionalProperties": False,
        },
    },
    {
        "name": "n8n_rest_set_workflow_active",
        "description": "Activate or deactivate an n8n workflow. Activation may cause production triggers to run.",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "minLength": 1, "description": "Workflow ID."},
                "active": {"type": "boolean", "description": "True to activate, false to deactivate."},
            },
            "required": ["workflow_id", "active"],
            "additionalProperties": False,
        },
    },
]
