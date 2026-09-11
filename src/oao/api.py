from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from oao.graph import build_graph


app = FastAPI()


class AnalyzeRequest(BaseModel):
    wallet_address: str


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    graph = build_graph()
    
    result = await graph.ainvoke(
        {
            "wallet_address": request.wallet_address,
        }
    )

    return jsonable_encoder(result)