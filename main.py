import os
from dotenv import load_dotenv
load_dotenv()
from oao.graph import build_graph


wallet_address = os.environ["WALLET_ADDRESS"]

app = build_graph()

result = app.invoke(
    {
        "wallet_address": wallet_address
    }
)

print(result)