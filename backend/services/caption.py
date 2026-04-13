import os

MODE = os.getenv("EMBEDDING_MODE", "mock")

if MODE == "openai":
    from services.providers.openai_provider import describe_image
elif MODE == "gemini":
    # try transcribe feature with gemini. fallback on openAI for now as flash in high demand
    #from services.providers.gemini_provider import describe_image
    from services.providers.openai_provider import describe_image
else:
    from services.providers.mock_provider import describe_image