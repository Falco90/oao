from langchain.chat_models import init_chat_model


model = init_chat_model(
    "qwen3.5:9b",
    model_provider="ollama",
    temperature=0,
    num_ctx=16384,
)