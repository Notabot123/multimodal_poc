import os
import numpy as np
import google.genai as genai
from google.genai.types import Content, Part

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-embedding-2-preview"
# or: "models/gemini-embedding-001"

def get_embedding(text: str = None, filepath: str = None, mime_type: str = None):
    try:
        # --- FILE / MULTIMODAL ---
        if filepath:
            with open(filepath, "rb") as f:
                data = f.read()

            response = client.models.embed_content(
                model=MODEL_NAME,
                contents=[
                    Content(
                        parts=[Part.from_bytes(data=data, mime_type=mime_type)]
                    )
                ]
            )

        # --- TEXT ---
        else:
            response = client.models.embed_content(
                model=MODEL_NAME,
                contents=[text]
            )

        # NEW RESPONSE FORMAT:
        vec = np.array(response.embeddings[0].values)
        return vec / np.linalg.norm(vec)

    except Exception as e:
        print(f"Gemini embedding error: {e}")
        raise
