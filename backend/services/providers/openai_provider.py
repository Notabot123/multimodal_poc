from openai import OpenAI
import base64
import mimetypes
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text: str):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def transcribe_audio(filepath: str) -> str:
    with open(filepath, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",  # modern whisper-based model
            file=audio_file
        )
    return transcript.text

def describe_image(filepath):
    print("absolute path:", os.path.abspath(filepath))
    print("exists:", os.path.exists(filepath))
    print("is file:", os.path.isfile(filepath))
    print("size:", os.path.getsize(filepath))
    mime, _ = mimetypes.guess_type(filepath)
    if mime is None:
        raise ValueError("Could not detect MIME type")
    print(f"mime: {mime}")

    with open(filepath, "rb") as f:
        image_bytes = f.read()
        print(f.read(8))

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{image_base64}"

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe this image briefly in no more than 2 sentences"},
                {"type": "input_image", "image_url": data_url}
            ]
        }]
    )

    return response.output_text