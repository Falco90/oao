from decimal import Decimal
from oao.state import Opportunity


RATE_TOLERANCE = Decimal("0.25")


def optimize_opportunities(
    opportunities: list[Opportunity],
) -> list[Opportunity]:
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

    return optimized