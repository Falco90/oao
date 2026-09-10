from oao.models.recommendation import Recommendation
from oao.models.llm import model
from oao.state import Opportunity, TokenHolding


async def generate_recommendation(
    holdings: list[TokenHolding],
    opportunities: list[Opportunity],
) -> Recommendation:
    structured_model = model.with_structured_output(
        Recommendation
    )

    prompt = f"""
    You are explaining lending opportunities for an Ethereum wallet.

    Wallet holdings:
    {holdings}

    Selected lending opportunities:
    {opportunities}

    Explain the selected opportunities clearly and concisely.

    Rules:
    - Treat the supplied holdings and opportunities as authoritative.
    - Do not invent protocols, rates, TVL, balances, or market data.
    - Do not perform new market discovery.
    - Do not choose different opportunities.
    - Explain why each selected opportunity is relevant to the wallet.
    - If the wallet contains native ETH and a selected opportunity uses WETH,
    explain that the ETH would need to be wrapped to WETH before it could
    be supplied to that market.
    - Do not claim that any opportunity is risk-free.
    - Do not say that unselected protocols or markets were not considered.
    You may say that the supplied opportunities are the final selected
    opportunities from the analysis.
    -- If an opportunity is marked active, describe it only as being
    reported as active in the supplied market data. Do not claim that
    deposits are guaranteed to be available at this moment.
    """

    return await structured_model.ainvoke(prompt)