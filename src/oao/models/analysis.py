from decimal import Decimal

from pydantic import BaseModel


class ProtocolAnalysis(BaseModel):
    protocol: str
    validated_subgraphs: list[str]
    market_count: int
    
class SelectionAnalysis(BaseModel):
    symbol: str
    selected_protocol: str
    selected_subgraph: str
    best_rate: Decimal
    selected_rate: Decimal
    selected_tvl_usd: Decimal
    competitive_market_count: int