from oao.state import AgentState
from oao.services.wallet import get_token_holdings


def analyze_wallet(state: AgentState) -> dict:
    holdings = get_token_holdings(state["wallet_address"])
    return {"holdings": holdings}