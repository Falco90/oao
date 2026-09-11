from langgraph.types import StreamWriter

from oao.services.discovery import discover_wallet_markets
from oao.state import AgentState


async def discover_opportunities(
    state: AgentState,
    writer: StreamWriter,
) -> dict:
    eligible_markets, protocol_analyses = (
        await discover_wallet_markets(
            state["holdings"],
            state["protocols"],
            writer,
        )
    )

    return {
        "eligible_markets": eligible_markets,
        "protocol_analyses": protocol_analyses,
    }