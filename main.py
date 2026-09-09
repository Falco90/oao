import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from oao.graph import build_graph


wallet_address = os.environ["WALLET_ADDRESS"]

async def main():
    app = build_graph()

    result = await app.ainvoke(
        {
            "wallet_address": wallet_address
        }
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())