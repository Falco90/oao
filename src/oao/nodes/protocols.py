from oao.services.discovery import discover_protocols
from oao.state import AgentState


async def discover_protocol_candidates(
    state: AgentState,
) -> dict:
    result = await discover_protocols(
        state["holdings"]
    )

    return {
        "protocols": result.protocols,
    }