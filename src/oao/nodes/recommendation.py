from oao.services.recommendation import generate_recommendation
from oao.state import AgentState


async def recommend(
    state: AgentState,
) -> dict:
    recommendation = await generate_recommendation(
        state["holdings"],
        state["opportunities"],
    )

    return {
        "recommendation": recommendation
    }