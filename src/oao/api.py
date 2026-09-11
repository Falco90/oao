from fastapi import FastAPI, HTTPException


from oao.graph import graph
from oao.models.api import (
    AnalyzeRequest,
    AnalyzeResponse,
    HoldingResponse,
    OpportunityResponse,
)


app = FastAPI()


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = await graph.ainvoke(
            {
                "wallet_address": request.wallet_address,
            }
        )
    except Exception as exc:
        print(f"Analysis failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "Analysis failed because an upstream "
                "service was unavailable."
            ),
        ) from exc

    return AnalyzeResponse(
        wallet_address=result["wallet_address"],
        holdings=[
            HoldingResponse(
                symbol=holding["symbol"],
                amount=str(holding["amount"]),
                network=holding["network"],
                contract_address=holding[
                    "contract_address"
                ],
            )
            for holding in result["holdings"]
        ],
        opportunities=[
            OpportunityResponse(
                protocol=opportunity["protocol"],
                subgraph_name=opportunity[
                    "subgraph_name"
                ],
                symbol=opportunity["symbol"],
                asset_address=opportunity[
                    "asset_address"
                ],
                market_id=opportunity["market_id"],
                tvl_usd=str(opportunity["tvl_usd"]),
                supply_rate=str(
                    opportunity["supply_rate"]
                ),
                is_active=opportunity["is_active"],
            )
            for opportunity in result["opportunities"]
        ],
        protocol_analyses=result["protocol_analyses"],
        selection_analyses=result[
            "selection_analyses"
        ],
        recommendation=result["recommendation"],
)