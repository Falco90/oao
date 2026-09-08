from oao.state import AgentState
from oao.services.wallet import get_wallet_holdings


def analyze_wallet(state: AgentState) -> dict:
    print(f"Analyzing wallet: {state['wallet_address']}")

    holdings = get_wallet_holdings(state["wallet_address"])

    return {"holdings": holdings}