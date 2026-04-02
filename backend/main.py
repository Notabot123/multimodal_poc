
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid, os, json
import numpy as np

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

def fake_embedding(text):
    vec = np.random.rand(384)
    return vec / np.linalg.norm(vec)

def cosine_similarity(a, b):
    return float(np.dot(a, b))

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    embedding = fake_embedding(file.filename)

    db.append({
        "id": file_id,
        "filename": file.filename,
        "filepath": filepath,
        "embedding": embedding.tolist(),
        "type": file.content_type
    })

    return {"id": file_id}

@app.post("/search")
async def search(query: str):
    query_emb = fake_embedding(query)

    results = []
    for item in db:
        score = cosine_similarity(query_emb, np.array(item["embedding"]))
        results.append({
            "id": item["id"],
            "filename": item["filename"],
            "type": item["type"],
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]


@app.get("/file/{file_id}")
def get_file(file_id: str):
    for item in db:
        if item["id"] == file_id:
            return FileResponse(item["filepath"])