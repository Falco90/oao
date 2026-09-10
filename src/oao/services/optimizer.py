from oao.state import Opportunity


def optimize_opportunities(
    opportunities: list[Opportunity],
) -> list[Opportunity]:
    best_by_symbol: dict[str, Opportunity] = {}

    for opportunity in opportunities:
        symbol = opportunity["symbol"]
        current_best = best_by_symbol.get(symbol)

        if (
            current_best is None
            or opportunity["supply_rate"]
            > current_best["supply_rate"]
        ):
            best_by_symbol[symbol] = opportunity

    return list(best_by_symbol.values())