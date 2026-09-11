from decimal import Decimal
from oao.models.analysis import SelectionAnalysis
from oao.state import Opportunity


RATE_TOLERANCE = Decimal("0.25")


def optimize_opportunities(
    opportunities: list[Opportunity],
) -> tuple[list[Opportunity], list[SelectionAnalysis]]:
    opportunities_by_symbol: dict[
        str,
        list[Opportunity],
    ] = {}

    for opportunity in opportunities:
        symbol = opportunity["symbol"]

        opportunities_by_symbol.setdefault(
            symbol,
            [],
        ).append(opportunity)

    optimized = []
    selection_analyses = []

    for symbol_opportunities in (
        opportunities_by_symbol.values()
    ):
        best_rate = max(
            opportunity["supply_rate"]
            for opportunity in symbol_opportunities
        )

        competitive = [
            opportunity
            for opportunity in symbol_opportunities
            if (
                best_rate
                - opportunity["supply_rate"]
                <= RATE_TOLERANCE
            )
        ]

        best = max(
            competitive,
            key=lambda opportunity: opportunity["tvl_usd"],
        )

        optimized.append(best)
        
        selection_analyses.append(
            SelectionAnalysis(
            symbol=best["symbol"],
            selected_protocol=best["protocol"],
            selected_subgraph=best["subgraph_name"],
            best_rate=best_rate,
            selected_rate=best["supply_rate"],
            selected_tvl_usd=best["tvl_usd"],
            competitive_market_count=len(competitive),
            )
        )

    return optimized, selection_analyses