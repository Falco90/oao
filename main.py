import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from oao.graph import build_graph
from pprint import pprint


wallet_address = os.environ["WALLET_ADDRESS"]

async def main():
    app = build_graph()

    result = await app.ainvoke(
        {
            "wallet_address": wallet_address
        }
    )

    pprint(result, sort_dicts=False, width=100)

if __name__ == "__main__":
    asyncio.run(main())