from openai import OpenAI
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
    with open(filepath, "rb") as f:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Describe this image briefly in no more than 2 sentences"},
                    {"type": "input_image", "image": f.read()}
                ]
            }]
        )
    return response.output_text