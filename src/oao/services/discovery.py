from dotenv import load_dotenv

load_dotenv()

from oao.models.discovery import ProtocolDiscovery, SubgraphCandidate
from oao.models.llm import model
from oao.state import TokenHolding
from oao.services.the_graph_mcp import search_subgraphs, get_subgraph_schema, get_deployment_query_counts

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
        
        protocol = result.protocols[0]
        
        search_result = await search_subgraphs(
            protocol
        )

        candidates = build_subgraph_candidates(
            protocol,
            search_result,
        )

        ethereum_candidates = filter_ethereum_candidates(
            protocol,
            candidates,
        )

        validated_candidates = await validate_subgraph_candidates(
            protocol,
            ethereum_candidates,
        )

        ipfs_hashes = [
            candidate.ipfs_hash
            for candidate in validated_candidates
        ]

        query_counts = await get_deployment_query_counts(
            ipfs_hashes
        )
        
        validated_candidates = attach_query_counts(
            validated_candidates,
            query_counts,
        )

        for candidate in validated_candidates:
            print(candidate)

    asyncio.run(main())