import os
import numpy as np
import google.genai as genai
from google.genai.types import Content, Part

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text: str = None, filepath: str = None, mime_type: str = None):
    """
    Unified embedding function for Gemini 2.
    - If `filepath` is provided → multimodal embedding
    - Else → text embedding
    """

    try:
        # --- FILE / MULTIMODAL ---
        if filepath:
            with open(filepath, "rb") as f:
                data = f.read()

            response = client.models.embed_content(
                model="models/text-embedding-004",
                contents=[
                    Content(
                        parts=[Part.from_bytes(data=data, mime_type=mime_type)]
                    )
                ]
            )

        # --- TEXT ---
        else:
            response = client.models.embed_content(
                model="models/text-embedding-004",
                contents=[text]
            )

        vec = np.array(response.embedding.values)
        return vec / np.linalg.norm(vec)

    except Exception as e:
        print(f"Gemini embedding error: {e}")
        raise
