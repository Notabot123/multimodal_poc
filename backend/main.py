
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid, os, json
import numpy as np
from dotenv import load_dotenv

load_dotenv()

from services.embedding import get_embedding
from services.speech import transcribe_audio, fake_transcribe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

db = []

def cosine_similarity(a, b):
    return float(np.dot(a, b))

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # modality handling
    if "audio" in file.content_type:
        try:
            text = transcribe_audio(filepath)
        except Exception as e:
            print(f"transcription failed: {e}")
            text = file.filename
    else:
        text = file.filename

    try:
        embedding = get_embedding(file.filename)
    except Exception as e:
        print(f"embedding failed. Error: {e}")

    db.append({
        "id": file_id,
        "filename": file.filename,
        "filepath": filepath,
        "embedding": embedding,
        "type": file.content_type,
        "text": text
    })

    return {"id": file_id}

@app.post("/search")
async def search(query: str = None, query_id: str = None):

    if query_id:
        # use embedding of selected file
        query_item = next((x for x in db if x["id"] == query_id), None)
        if not query_item:
            return []

        query_emb = np.array(query_item["embedding"])

    else:
        # fallback to text query
        try:
            query_emb = get_embedding(query)
        except Exception as e:
            print("embedding failed. Error: {e}")

    results = []
    for item in db:
        score = cosine_similarity(query_emb, np.array(item["embedding"]))
        results.append({
            "id": item["id"],
            "filename": item["filename"],
            "type": item["type"],
            "score": score,
            "text": item.get("text", "")
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]


@app.get("/file/{file_id}")
def get_file(file_id: str):
    for item in db:
        if item["id"] == file_id:
            return FileResponse(item["filepath"])