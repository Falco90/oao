from pydantic import BaseModel, Field


class ProtocolDiscovery(BaseModel):
    protocols: list[str] = Field(
        description=(
            "Ethereum lending protocols relevant to the supplied "
            "wallet holdings."
        )
    )
    
class SubgraphCandidate(BaseModel):
    protocol: str
    subgraph_id: str
    ipfs_hash: str
    display_name: str