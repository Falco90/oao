from pydantic import BaseModel, Field


class ProtocolDiscovery(BaseModel):
    protocols: list[str] = Field(
        description=(
            "Ethereum lending protocols relevant to the supplied "
            "wallet holdings."
        )
    )