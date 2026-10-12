"""Hermes n8n REST API plugin.

MCP remains the recommended primary integration. These tools provide a
complementary path through n8n's public REST API.
"""
from . import schemas, tools


def register(ctx):
    for item in schemas.ALL_SCHEMAS:
        tool_schema = {
            **item["parameters"],
            "description": item["description"],
        }

        ctx.register_tool(
            name=item["name"],
            toolset="n8n_rest",
            schema=tool_schema,
            handler=tools.HANDLERS[item["name"]],
            emoji="🔁",
        )
