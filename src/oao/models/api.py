from pydantic import BaseModel, field_validator

from oao.models.analysis import (
    ProtocolAnalysis,
    SelectionAnalysis,
)
from oao.models.recommendation import Recommendation


class AnalyzeRequest(BaseModel):
    wallet_address: str

    @field_validator("wallet_address")
    @classmethod
    def validate_wallet_address(cls, value: str) -> str:
        if (
            not value.startswith("0x")
            or len(value) != 42
        ):
            raise ValueError(
                "Invalid Ethereum wallet address"
            )

        try:
            int(value[2:], 16)
        except ValueError:
            raise ValueError(
                "Invalid Ethereum wallet address"
            )

        return value
    
    
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