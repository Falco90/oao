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
        
async def get_subgraph_schema(subgraph_id: str) -> str:
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
                "get_schema_by_subgraph_id",
                arguments={
                    "subgraph_id": subgraph_id,
                },
            )

            return result.content[0].text
        

async def get_deployment_query_counts(
    ipfs_hashes: list[str],
) -> dict:
    api_key = os.environ["THE_GRAPH_GATEWAY_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}

    async with sse_client(
        MCP_URL,
        headers=headers,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "get_deployment_30day_query_counts",
                arguments={
                    "ipfs_hashes": ipfs_hashes,
                },
            )

            return json.loads(result.content[0].text)