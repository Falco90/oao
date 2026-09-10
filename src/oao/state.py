from decimal import Decimal
from typing import TypedDict


class TokenHolding(TypedDict):
    symbol: str
    amount: Decimal
    network: str
    contract_address: str | None


class Opportunity(TypedDict):
    protocol: str
    symbol: str
    asset_address: str
    market_id: str
    tvl_usd: Decimal
    supply_rate: Decimal
    is_active: bool


class AgentState(TypedDict):
    wallet_address: str
    holdings: list[TokenHolding]
    opportunities: list[Opportunity]