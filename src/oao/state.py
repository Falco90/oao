from typing import TypedDict


class TokenHolding(TypedDict):
    symbol: str
    amount: float
    network: str
    contract_address: str | None


class AgentState(TypedDict):
    wallet_address: str
    holdings: list[TokenHolding]