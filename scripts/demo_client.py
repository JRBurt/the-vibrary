"""Stand-in for what Claude Code (or any MCP client) does: launch the server
as a subprocess over stdio, discover its tools, then call one.

Run with: python -m scripts.demo_client
"""

import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools the server advertises:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.strip().splitlines()[0]}")
            print()

            print("Calling list_collections...")
            result = await session.call_tool("list_collections", {})
            print(" ->", result.structured_content or [c.text for c in result.content])
            print()

            query = "how should I review code for bugs"
            print(f"Calling search(query={query!r})...")
            result = await session.call_tool("search", {"query": query, "top_k": 2})
            print(" ->", result.structured_content or [c.text for c in result.content])


if __name__ == "__main__":
    asyncio.run(main())
