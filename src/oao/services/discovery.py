from dotenv import load_dotenv

load_dotenv()

from oao.models.discovery import ProtocolDiscovery
from oao.models.llm import model
from oao.state import TokenHolding
from oao.services.the_graph_mcp import search_subgraphs

async def discover_protocols(
    holdings: list[TokenHolding],
) -> ProtocolDiscovery:
    structured_model = model.with_structured_output(
        ProtocolDiscovery
    )

    prompt = f"""
            You are helping identify Ethereum mainnet lending protocols
            that may be relevant for a user's wallet holdings.

            Wallet holdings:
            {holdings}

            Identify a broad but relevant set of Ethereum mainnet lending protocols
            that could offer lending, supply-yield, or collateralized borrowing
            opportunities for these assets.

            Include established protocols even if their lending model differs from
            pooled money markets.

            Return canonical protocol names only.
            Do not include versions, networks, product descriptions, or commentary.
            Do not calculate yields.
            Do not recommend allocations.
            Do not invent subgraph IDs.
            """

    return await structured_model.ainvoke(prompt)

if __name__ == "__main__":
    import asyncio
    from decimal import Decimal
    from pprint import pprint

    async def main():
        holdings: list[TokenHolding] = [
            {
                "symbol": "USDC",
                "amount": Decimal("100"),
                "network": "mainnet",
                "contract_address": (
                    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
                ),
            },
            {
                "symbol": "WETH",
                "amount": Decimal("1"),
                "network": "mainnet",
                "contract_address": (
                    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
                ),
            },
        ]

        result = await discover_protocols(holdings)
        
        mcp_result = await search_subgraphs(
            result.protocols[0]
        )

        pprint(mcp_result)


    asyncio.run(main())