import os
import numpy as np
import mimetypes
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
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

    except Exception as e:
        print(f"Gemini embedding error: {e}")
        raise

def describe_image(filepath: str) -> str:
    try:
        mime, _ = mimetypes.guess_type(filepath)
        if mime is None:
            raise ValueError("Could not detect MIME type")

        with open(filepath, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                Content(
                    parts=[
                        Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime
                        ),
                        Part.from_text(text="Transcribe this audio accurately.")
                    ]
                )
            ]
        )

        return response.candidates[0].content.parts[0].text #return response.text

    except Exception as e:
        print(f"Gemini image error: {e}")
        raise

def transcribe_audio(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            audio_bytes = f.read()

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                Content(
                    parts=[
                        Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/wav"  # adjust if needed
                        ),
                        Part.from_text("Transcribe this audio accurately.")
                    ]
                )
            ]
        )

        return response.candidates[0].content.parts[0].text #return response.text

    except Exception as e:
        print(f"Gemini transcription error: {e}")
        raise