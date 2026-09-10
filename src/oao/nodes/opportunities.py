from oao.services.discovery import discover_wallet_markets
from oao.state import AgentState


async def discover_opportunities(state: AgentState) -> dict:
    opportunities = await discover_wallet_markets(
        state["holdings"]
    )

    return {
        "opportunities": opportunities
    }