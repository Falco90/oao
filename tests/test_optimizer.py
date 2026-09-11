from decimal import Decimal

from oao.services.optimizer import optimize_opportunities


def test_optimizer_prefers_liquidity_within_rate_tolerance():
    opportunities = [
        {
            "protocol": "Protocol A",
            "subgraph_name": "A Ethereum",
            "symbol": "USDC",
            "asset_address": "0x1",
            "market_id": "market-a",
            "tvl_usd": Decimal("2000000"),
            "supply_rate": Decimal("5.10"),
            "is_active": True,
        },
        {
            "protocol": "Protocol B",
            "subgraph_name": "B Ethereum",
            "symbol": "USDC",
            "asset_address": "0x2",
            "market_id": "market-b",
            "tvl_usd": Decimal("400000000"),
            "supply_rate": Decimal("5.02"),
            "is_active": True,
        },
        {
            "protocol": "Protocol C",
            "subgraph_name": "C Ethereum",
            "symbol": "USDC",
            "asset_address": "0x3",
            "market_id": "market-c",
            "tvl_usd": Decimal("2000000000"),
            "supply_rate": Decimal("4.70"),
            "is_active": True,
        },
    ]

    result, analyses = optimize_opportunities(
        opportunities
    )

    assert len(result) == 1
    assert result[0]["protocol"] == "Protocol B"

    assert len(analyses) == 1

    analysis = analyses[0]

    assert analysis.symbol == "USDC"
    assert analysis.selected_protocol == "Protocol B"
    assert analysis.selected_subgraph == "B Ethereum"
    assert analysis.best_rate == Decimal("5.10")
    assert analysis.selected_rate == Decimal("5.02")
    assert analysis.selected_tvl_usd == Decimal(
        "400000000"
    )
    assert analysis.competitive_market_count == 2
    

def test_optimizer_prefers_higher_rate_outside_tolerance():
    opportunities = [
        {
            "protocol": "Protocol A",
            "subgraph_name": "A Ethereum",
            "symbol": "USDC",
            "asset_address": "0x1",
            "market_id": "market-a",
            "tvl_usd": Decimal("2000000"),
            "supply_rate": Decimal("5.10"),
            "is_active": True,
        },
        {
            "protocol": "Protocol B",
            "subgraph_name": "B Ethereum",
            "symbol": "USDC",
            "asset_address": "0x2",
            "market_id": "market-b",
            "tvl_usd": Decimal("1000000000"),
            "supply_rate": Decimal("4.80"),
            "is_active": True,
        },
    ]

    result, analyses = optimize_opportunities(
        opportunities
    )

    assert len(result) == 1
    assert result[0]["protocol"] == "Protocol A"

    assert len(analyses) == 1

    analysis = analyses[0]

    assert analysis.symbol == "USDC"
    assert analysis.selected_protocol == "Protocol A"
    assert analysis.selected_subgraph == "A Ethereum"
    assert analysis.best_rate == Decimal("5.10")
    assert analysis.selected_rate == Decimal("5.10")
    assert analysis.selected_tvl_usd == Decimal(
        "2000000"
    )
    assert analysis.competitive_market_count == 1