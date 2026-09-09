import os

from oao.services.aave import discover_aave_opportunities
from oao.state import AgentState


async def discover_opportunities(state: AgentState) -> dict:
    api_key = os.environ["THE_GRAPH_GATEWAY_API_KEY"]

    opportunities = await discover_aave_opportunities(
        holdings=state["holdings"],
        api_key=api_key,
    )

    return {
        "opportunities": opportunities,
    }