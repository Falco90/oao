from oao.services.optimizer import optimize_opportunities
from oao.state import AgentState


def optimize_eligible_markets(
    state: AgentState,
) -> dict:
    opportunities, selection_analyses = (
        optimize_opportunities(
            state["eligible_markets"]
        )
    )

    return {
        "opportunities": opportunities,
        "selection_analyses": selection_analyses,
    }