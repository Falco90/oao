from oao.services.discovery import discover_wallet_markets
from oao.state import AgentState


async def discover_opportunities(state: AgentState) -> dict:
    opportunities, protocol_analyses, selection_analyses = await discover_wallet_markets(
        state["holdings"]
    )
    
    return {
        "opportunities": opportunities,
        "protocol_analyses": protocol_analyses,
        "selection_analyses": selection_analyses
    }