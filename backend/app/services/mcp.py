import json

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters
)


def get_server_params():

    return StdioServerParameters(
        command="python",
        args=[
            "app/mcp/server.py"
        ],
    )


async def get_mcp_tools():

    server_params = get_server_params()

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()

            result = await session.list_tools()

            return result.tools



async def execute_mcp_tool(
    tool_name: str,
    arguments: dict
):

    server_params = get_server_params()

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()


            result = await session.call_tool(
                tool_name,
                arguments
            )


            content = result.content[0].text


            try:
                return json.loads(content)

            except json.JSONDecodeError:

                return {
                    "message": content
                }