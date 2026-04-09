import os
import numpy as np
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_embedding_from_file(filepath: str, mime_type: str):
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        response = genai.embed_content(
            model="models/embedding-001",
            content={
                "mime_type": mime_type,
                "data": content
            }
        )

        vec = np.array(response["embedding"])
        return vec / np.linalg.norm(vec)

    except Exception as e:
        print(f"Gemini multimodal embedding error: {e}")
        raise


def get_embedding(text: str):
    # fallback for text queries
    response = genai.embed_content(
        model="models/embedding-001",
        content=text
    )

    vec = np.array(response["embedding"])
    return vec / np.linalg.norm(vec)