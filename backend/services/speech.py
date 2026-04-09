import os

MODE = os.getenv("EMBEDDING_MODE", "mock")

if MODE == "openai":
    from services.providers.openai_provider import transcribe_audio
elif MODE == "gemini":
    from services.providers.gemini_provider import transcribe_audio
else:
    from services.providers.mock_provider import transcribe_audio