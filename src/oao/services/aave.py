import json

from decimal import Decimal

from mcp import ClientSession
from mcp.client.sse import sse_client

from oao.state import TokenHolding


AAVE_V3_ETHEREUM_IPFS = (
    "QmcXE5QVcBcvcaJddPxd8mFs6W9xt7STmwfgguoiM6ddAd"
)


def normalize_market(market: dict) -> dict:
    token = market["inputToken"]

    decimals = token["decimals"]

    amount = Decimal(market["inputTokenBalance"]) / (
        Decimal(10) ** decimals
    )

    supply_rate = next(
        Decimal(rate["rate"])
        for rate in market["rates"]
        if rate["side"] == "LENDER"
        and rate["type"] == "VARIABLE"
    )

    return {
        "protocol": "Aave",
        "symbol": token["symbol"],
        "asset_address": token["id"],
        "market_id": market["id"],
        "amount": amount,
        "tvl_usd": Decimal(market["totalValueLockedUSD"]),
        "supply_rate": supply_rate,
        "is_active": market["isActive"],
        "can_borrow": market["canBorrowFrom"],
        "can_use_as_collateral": market["canUseAsCollateral"],
    }

def match_holdings_to_markets(
    holdings: list[TokenHolding],
    markets: list[dict],
) -> list[dict]:
    opportunities = []

    for holding in holdings:
        for market in markets:
            if holding["contract_address"] == market["asset_address"]:
                opportunities.append(
                    {
                        "holding": holding,
                        "market": market,
                    }
                )

    return opportunities



def build_opportunity(match: dict) -> dict:
    holding = match["holding"]
    market = match["market"]

    return {
        "protocol": market["protocol"],
        "symbol": market["symbol"],
        "asset_address": market["asset_address"],
        "market_id": market["market_id"],
        "holding_amount": holding["amount"],
        "market_amount": market["amount"],
        "tvl_usd": market["tvl_usd"],
        "supply_rate": market["supply_rate"],
        "is_active": market["is_active"],
        "can_borrow": market["can_borrow"],
        "can_use_as_collateral": market["can_use_as_collateral"],
    }
    
    
async def discover_aave_opportunities(
    holdings: list[TokenHolding],
    api_key: str,
) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    async with sse_client(
        "https://subgraphs.mcp.thegraph.com/sse",
        headers=headers,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "execute_query_by_ipfs_hash",
                arguments={
                    "ipfs_hash": AAVE_V3_ETHEREUM_IPFS,
                    "query": """
                    {
                      markets(first: 50) {
                        id
                        name
                        isActive
                        canBorrowFrom
                        canUseAsCollateral
                        inputToken {
                          symbol
                          name
                          decimals
                          id
                        }
                        inputTokenBalance
                        inputTokenPriceUSD
                        totalValueLockedUSD
                        totalBorrowBalanceUSD
                        rates {
                          rate
                          duration
                          side
                          type
                        }
                      }
                    }
                    """,
                },
            )

            data = json.loads(result.content[0].text)

            markets = data["data"]["markets"]

            normalized_markets = [
                normalize_market(market)
                for market in markets
            ]
            
            supported_symbols = {"USDC", "USDT", "WETH"}

            supported_markets = [
                market
                for market in normalized_markets
                if market["symbol"] in supported_symbols
            ]

            matches = match_holdings_to_markets(
                holdings,
                supported_markets,
            )

            opportunities = [
                build_opportunity(match)
                for match in matches
            ]

            return opportunities
        

if __name__ == "__main__":
    import asyncio
    import os

    from dotenv import load_dotenv
    from oao.services.wallet import get_token_holdings

    load_dotenv()

    wallet_address = "0x42e02FB5aF30aa379314371ADa1e3035967B569B"
    api_key = os.environ["THE_GRAPH_GATEWAY_API_KEY"]

    holdings = get_token_holdings(wallet_address)

    opportunities = asyncio.run(
        discover_aave_opportunities(
            holdings=holdings,
            api_key=api_key,
        )
    )

    print("\n=== OPPORTUNITIES ===")
    print(opportunities)