import json
import os

from mcp import ClientSession
from mcp.client.sse import sse_client


MCP_URL = "https://subgraphs.mcp.thegraph.com/sse"


async def search_subgraphs(keyword: str) -> dict:
    api_key = os.environ["THE_GRAPH_GATEWAY_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    async with sse_client(
        MCP_URL,
        headers=headers,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "search_subgraphs_by_keyword",
                arguments={
                    "keyword": keyword,
                },
            )

            return json.loads(result.content[0].text)