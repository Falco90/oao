from pydantic import BaseModel

from oao.models.analysis import (
    ProtocolAnalysis,
    SelectionAnalysis,
)
from oao.models.recommendation import Recommendation

from typing import Annotated

from fastapi import Query


WalletAddress = Annotated[
    str,
    Query(
        pattern=r"^0x[a-fA-F0-9]{40}$",
        description="Ethereum wallet address",
    ),
]

    
class HoldingResponse(BaseModel):
    symbol: str
    amount: str
    network: str
    contract_address: str | None


class OpportunityResponse(BaseModel):
    protocol: str
    subgraph_name: str
    symbol: str
    asset_address: str
    market_id: str
    tvl_usd: str
    supply_rate: str
    is_active: bool


class AnalyzeResponse(BaseModel):
    wallet_address: str
    holdings: list[HoldingResponse]
    opportunities: list[OpportunityResponse]
    protocol_analyses: list[ProtocolAnalysis]
    selection_analyses: list[SelectionAnalysis]
    recommendation: Recommendation