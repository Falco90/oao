import os
import requests
from oao.state import TokenHolding


def get_wallet_holdings(wallet_address: str) -> list[TokenHolding]:
    api_url = os.environ["THE_GRAPH_API_URL"]
    jwt_token = os.environ["THE_GRAPH_API_JWT_TOKEN"]
    
    response = requests.get(f"{api_url}/evm/balances",
        params={
            "network": "mainnet",
            "address": wallet_address,
            "limit": 10,
            "page": 1,
        },
        headers={
            "Authorization": f"Bearer {jwt_token}",
        },
        timeout=30,
    )
    
    response.raise_for_status()

    data = response.json()
    
    return _normalize_holdings(data["data"])

def _normalize_holdings(data: dict) -> list[TokenHolding]:
    holdings: list[TokenHolding] = []

    for token in data:
        holdings.append(
            {
                "symbol": token["symbol"],
                "amount": float(token["value"]),
                "network": token["network"],
                "contract_address": token["contract"],
            }
        )

    return holdings