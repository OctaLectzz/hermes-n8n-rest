"""Hermes n8n REST API plugin.

MCP remains the recommended primary integration. These tools provide a
complementary path through n8n's public REST API.
"""
from . import schemas, tools


def register(ctx):
    for schema in schemas.ALL_SCHEMAS:
        ctx.register_tool(
            name=schema["name"],
            toolset="n8n_rest",
            schema=schema,
            handler=tools.HANDLERS[schema["name"]],
            emoji="🔁",
        )
