from pydantic import BaseModel


class ProtocolAnalysis(BaseModel):
    protocol: str
    validated_subgraphs: list[str]
    market_count: int