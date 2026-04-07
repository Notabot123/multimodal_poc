from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(filepath: str) -> str:
    with open(filepath, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",  # modern whisper-based model
            file=audio_file
        )
    return transcript.text

def fake_transcribe(filepath: str) -> str:
    # if no API service for demo
    filename = os.path.basename(filepath).lower()
        
    return f"audio recording of {filename}"