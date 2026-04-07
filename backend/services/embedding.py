import os

MODE = os.getenv("EMBEDDING_MODE", "mock")
print(f"Running in {MODE.upper()} mode")

if MODE == "openai":
    from services.providers.openai_provider import get_embedding
elif MODE == "gemini":
    from services.providers.gemini_provider import get_embedding
else:
    from services.providers.mock_provider import get_embedding