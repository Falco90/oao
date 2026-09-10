from dotenv import load_dotenv

load_dotenv()

from decimal import Decimal
from oao.models.discovery import ProtocolDiscovery, SubgraphCandidate
from oao.models.llm import model
from oao.state import TokenHolding
from oao.services.the_graph_mcp import execute_subgraph_query, search_subgraphs, get_subgraph_schema, get_deployment_query_counts
from oao.services.wallet import get_token_holdings

WETH_MAINNET = (
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
)

MIN_TVL_USD = Decimal("1000000")

def get_holding_market_address(
    holding: TokenHolding,
) -> str | None:
    if (
        holding["network"] == "mainnet"
        and holding["symbol"] == "ETH"
        and holding["contract_address"] is None
    ):
        return WETH_MAINNET

    return holding["contract_address"]


def build_market_query(
    first: int,
    skip: int,
) -> str:
    return f"""
    {{
      markets(first: {first}, skip: {skip}) {{
        id
        name
        isActive
        totalValueLockedUSD
        inputToken {{
          id
          symbol
        }}
        rates {{
          rate
          side
          type
        }}
      }}
    }}
    """
    

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

async def discover_protocol_markets(
    protocol: str,
) -> list[dict]:
    keywords = [
        protocol,
        f"{protocol} V3",
    ]

    all_subgraphs = []

    for keyword in keywords:
        result = await search_subgraphs(keyword)
        all_subgraphs.extend(result["subgraphs"])

    unique_subgraphs = {
        subgraph["id"]: subgraph
        for subgraph in all_subgraphs
    }.values()

    merged_result = {
        "subgraphs": list(unique_subgraphs)
    }

    candidates = build_subgraph_candidates(
        protocol,
        merged_result,
    )

    ethereum_candidates = filter_ethereum_candidates(
        protocol,
        candidates,
    )

    validated_candidates = await validate_subgraph_candidates(
        protocol,
        ethereum_candidates,
    )
    
    print(
        protocol,
        "validated:",
        [
            candidate.display_name
            for candidate in validated_candidates
        ],
    )

    normalized_markets = []

    for candidate in validated_candidates:
        markets = await fetch_all_markets(
            candidate.subgraph_id
        )

        for market in markets:
            if market["inputToken"]["symbol"] not in {
                "USDC",
                "USDT",
                "WETH",
            }:
                continue

            normalized_markets.append(
                normalize_discovered_market(
                    protocol=candidate.protocol,
                    subgraph_name=candidate.display_name,
                    market=market,
                )
            )

    return normalized_markets


def build_subgraph_candidates(
    protocol: str,
    search_result: dict,
) -> list[SubgraphCandidate]:
    candidates = []

    for subgraph in search_result["subgraphs"]:
        deployment = subgraph.get("currentVersion", {}).get(
            "subgraphDeployment",
            {},
        )

        ipfs_hash = deployment.get("ipfsHash")

        if not ipfs_hash:
            continue

        candidates.append(
            SubgraphCandidate(
                protocol=protocol,
                subgraph_id=subgraph["id"],
                ipfs_hash=ipfs_hash,
                display_name=subgraph["metadata"]["displayName"].strip(),
            )
        )

    return candidates


async def fetch_all_markets(
    subgraph_id: str,
) -> list[dict]:
    markets = []
    page_size = 100
    skip = 0

    while True:
        query = build_market_query(
            first=page_size,
            skip=skip,
        )

        result = await execute_subgraph_query(
            subgraph_id,
            query,
        )

        page = result["data"]["markets"]

        if not page:
            break

        markets.extend(page)
        skip += page_size

    return markets


def filter_ethereum_candidates(
    protocol: str,
    candidates: list[SubgraphCandidate],
) -> list[SubgraphCandidate]:
    protocol_name = protocol.lower()

    filtered = []

    for candidate in candidates:
        name = candidate.display_name.lower()

        if "ethereum" not in name:
            continue

        if protocol_name not in name:
            continue

        filtered.append(candidate)

    return filtered


def is_lending_schema(schema: str) -> bool:
    required_markers = [
        "type Market",
        "rates:",
        "totalValueLockedUSD",
        "type Position",
        "side: PositionSide",
    ]

    return all(marker in schema for marker in required_markers)


def matches_protocol_identity(
    protocol: str,
    candidate: SubgraphCandidate,
) -> bool:
    name = candidate.display_name.lower()
    protocol_name = protocol.lower()

    return name.startswith(protocol_name)


async def validate_subgraph_candidates(
    protocol: str,
    candidates: list[SubgraphCandidate],
) -> list[SubgraphCandidate]:
    validated = []

    for candidate in candidates:
        if not matches_protocol_identity(protocol, candidate):
            continue

        schema = await get_subgraph_schema(
            candidate.subgraph_id
        )

        if not is_lending_schema(schema):
            continue

        validated.append(candidate)

    return validated


def attach_query_counts(
    candidates: list[SubgraphCandidate],
    query_counts: dict,
) -> list[SubgraphCandidate]:
    counts_by_ipfs = {
        deployment["ipfs_hash"]: deployment["total_query_count"]
        for deployment in query_counts["deployments"]
    }

    for candidate in candidates:
        candidate.query_count_30d = counts_by_ipfs.get(
            candidate.ipfs_hash
        )

    return candidates


def get_lender_variable_rate(market: dict) -> Decimal | None:
    for rate in market["rates"]:
        if (
            rate["side"] == "LENDER"
            and rate["type"] == "VARIABLE"
        ):
            return Decimal(rate["rate"])

    return None


def normalize_discovered_market(
    protocol: str,
    subgraph_name: str,
    market: dict,
) -> dict:
    return {
        "protocol": protocol,
        "subgraph_name": subgraph_name,
        "symbol": market["inputToken"]["symbol"],
        "asset_address": market["inputToken"]["id"],
        "market_id": market["id"],
        "tvl_usd": Decimal(market["totalValueLockedUSD"]),
        "supply_rate": get_lender_variable_rate(market),
        "is_active": market["isActive"],
    }
    

def filter_eligible_markets(
    markets: list[dict],
) -> list[dict]:
    return [
        market
        for market in markets
        if market["is_active"]
        and market["supply_rate"] is not None
        and market["supply_rate"] > 0
        and market["tvl_usd"] >= MIN_TVL_USD
    ]
    
    
def select_best_markets(
    eligible_markets: list[dict],
) -> dict[str, dict]:
    best_markets = {}

    for market in eligible_markets:
        symbol = market["symbol"]
        current_best = best_markets.get(symbol)

        if (
            current_best is None
            or market["supply_rate"] > current_best["supply_rate"]
        ):
            best_markets[symbol] = market

    return best_markets


def match_markets_to_holdings(
    markets: list[dict],
    holdings: list[TokenHolding],
) -> list[dict]:
    holding_addresses = {
        address.lower()
        for holding in holdings
        if (
            address := get_holding_market_address(
                holding
            )
        )
    }

    return [
        market
        for market in markets
        if market["asset_address"].lower()
        in holding_addresses
    ]
    
async def discover_wallet_markets(
    holdings: list[TokenHolding],
) -> dict[str, dict]:
    protocol_discovery = await discover_protocols(
        holdings
    )

    all_markets = []

    for protocol in protocol_discovery.protocols:
        print(f"\n--- Discovering {protocol} ---")

        try:
            markets = await discover_protocol_markets(
                protocol
            )
        except Exception as exc:
            print(
                f"{protocol}: discovery failed: {exc}"
            )
            continue

        print(
            f"{protocol}: {len(markets)} markets"
        )

        all_markets.extend(markets)

    eligible_markets = filter_eligible_markets(
        all_markets
    )

    matched_markets = match_markets_to_holdings(
        eligible_markets,
        holdings,
    )

    return select_best_markets(
        matched_markets
    )
    
    
if __name__ == "__main__":
    import asyncio
    from decimal import Decimal

    async def main():
        wallet_address = "0xad4010aC206b14D66999b4BF9b80C6bc97B60b9A"

        holdings = get_token_holdings(
            wallet_address
        )

        print("\n--- Holdings ---")
        for holding in holdings:
            print(
                holding["symbol"],
                holding["amount"],
                holding["contract_address"],
            )

        best_markets = await discover_wallet_markets(
            holdings
        )

        print("\n--- Best Markets ---")
        for symbol, market in best_markets.items():
            print(
                symbol,
                market["protocol"],
                market["subgraph_name"],
                market["supply_rate"],
                market["tvl_usd"],
            )


if __name__ == "__main__":
    asyncio.run(main())