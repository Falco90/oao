import os
import requests
from oao.state import TokenHolding
from oao.config.tokens import SUPPORTED_TOKEN_ADDRESSES


def get_token_holdings(wallet_address: str) -> list[TokenHolding]:
    token_data = _get_token_balances(wallet_address)
    native_data = _get_native_balance(wallet_address)

    token_data = _filter_supported_tokens(token_data)

    return _normalize_token_holdings(token_data, native_data)


def _get_token_balances(wallet_address: str) -> list[dict]:
    all_tokens = []
    page = 1

    while True:
        response = requests.get(
            f"{os.environ["THE_GRAPH_API_URL"]}/evm/balances",
            params={
                "network": "mainnet",
                "address": wallet_address,
                "limit": 10,
                "page": page,
            },
            headers={
                "Authorization": f"Bearer {os.environ['THE_GRAPH_API_JWT_TOKEN']}",
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        tokens = data["data"]

        if not tokens:
            break

        all_tokens.extend(tokens)
        page += 1

    return all_tokens


def _get_native_balance(wallet_address: str) -> dict:
    response = requests.get(
        f"{os.environ["THE_GRAPH_API_URL"]}/evm/balances/native",
        params={
            "network": "mainnet",
            "address": wallet_address,
        },
        headers={
            "Authorization": f"Bearer {os.environ['THE_GRAPH_API_JWT_TOKEN']}",
        },
        timeout=30,
    )

    response.raise_for_status()
    
    data = response.json()["data"]
    
    return data


def _normalize_token_holdings(
    token_data: list[dict],
    native_data: dict,
) -> list[TokenHolding]:
    holdings: list[TokenHolding] = []
    for token in token_data:
        holdings.append(
            {
                "symbol": token["symbol"],
                "amount": float(token["value"]),
                "chain": token["network"],
                "contract_address": token["contract"],
            }
        )
    
    for token in native_data:
        holdings.append(
            {
                "symbol": token["symbol"],
                "amount": float(token["value"]),
                "chain": token["network"],
                "contract_address": None,
            }
        )
        
    return holdings


def _filter_supported_tokens(tokens: list[dict]) -> list[dict]:
    return [
        token
        for token in tokens
        if token["contract"].lower() in SUPPORTED_TOKEN_ADDRESSES[token["network"]]
    ]