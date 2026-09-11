import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder

from oao.graph import graph
from oao.models.api import (
    AnalyzeResponse,
    HoldingResponse,
    OpportunityResponse,
    WalletAddress
)

PROGRESS_MESSAGES = {
    "analyze_wallet": "Wallet analyzed",
    "discover_protocol_candidates": "Lending protocols discovered",
    "discover_opportunities": "Markets discovered and filtered",
    "optimize_eligible_markets": "Best opportunities selected",
    "recommend": "Recommendation generated",
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
@app.get("/analyze")
async def analyze_stream(wallet_address: WalletAddress):
    async def event_stream():
        final_state = {
            "wallet_address": wallet_address,
        }
        
        async for update in graph.astream(
            {
                "wallet_address": wallet_address,
            },
            stream_mode="updates",
        ):
            for node_name, node_output in update.items():
                final_state.update(node_output)

                event = {
                    "type": "progress",
                    "stage": node_name,
                    "message": PROGRESS_MESSAGES.get(
                        node_name,
                        node_name,
                    ),
                }
                
                if node_name == "analyze_wallet":
                    event["data"] = {
                        "holdings": [
                            {
                                "symbol": holding["symbol"],
                                "amount": str(holding["amount"]),
                                "network": holding["network"],
                                "contract_address": holding[
                                    "contract_address"
                                ],
                            }
                            for holding in node_output["holdings"]
                        ]
                    }
                    
                if node_name == "discover_protocol_candidates":
                    event["data"] = {
                        "protocols": node_output["protocols"],
                    }
                    
                if node_name == "discover_opportunities":
                    event["data"] = {
                        "protocol_analyses": [
                            analysis.model_dump()
                            for analysis in node_output[
                                "protocol_analyses"
                            ]
                        ],
                    }

                yield f"data: {json.dumps(event)}\n\n"

        response = build_analyze_response(final_state)

        complete_event = {
            "type": "complete",
            "data": jsonable_encoder(response),
        }

        yield (
            f"data: {json.dumps(complete_event)}\n\n"
        )
        
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
    
    
def build_analyze_response(
    result: dict,
) -> AnalyzeResponse:
    return AnalyzeResponse(
        wallet_address=result["wallet_address"],
        holdings=[
            HoldingResponse(
                symbol=holding["symbol"],
                amount=str(holding["amount"]),
                network=holding["network"],
                contract_address=holding["contract_address"],
            )
            for holding in result["holdings"]
        ],
        opportunities=[
            OpportunityResponse(
                protocol=opportunity["protocol"],
                subgraph_name=opportunity["subgraph_name"],
                symbol=opportunity["symbol"],
                asset_address=opportunity["asset_address"],
                market_id=opportunity["market_id"],
                tvl_usd=str(opportunity["tvl_usd"]),
                supply_rate=str(opportunity["supply_rate"]),
                is_active=opportunity["is_active"],
            )
            for opportunity in result["opportunities"]
        ],
        protocol_analyses=result["protocol_analyses"],
        selection_analyses=result["selection_analyses"],
        recommendation=result["recommendation"],
    )