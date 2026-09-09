from oao.state import AgentState


def filter_opportunities(state: AgentState) -> dict:
    eligible = [
        opportunity
        for opportunity in state["opportunities"]
        if opportunity["is_active"]
    ]

    return {
        "opportunities": eligible,
    }