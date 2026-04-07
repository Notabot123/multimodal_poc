from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def fake_embedding(text):
    """ just placeholder, delete when real embedding available """
    vec = np.random.rand(384)
    return vec / np.linalg.norm(vec)