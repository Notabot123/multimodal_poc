from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid, os, json
import numpy as np
from dotenv import load_dotenv

load_dotenv()
MODE = os.getenv("EMBEDDING_MODE", "mock")

from services.embedding import get_embedding
   
from services.speech import transcribe_audio
from services.caption import describe_image
from services.vector_store import build_index, load_index
from services.vector_store import search as faiss_search
from services.db import db
from api.visualise import router as visualise_router

app = FastAPI()

#  fast lookup map
db_map = {item["id"]: item for item in db}

INDEX_FILE = "faiss.index"
#  load FAISS index if exists
if os.path.exists(INDEX_FILE):
    load_index(db)
else:
    print("No index file found, rebuilding")
    build_index(db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(visualise_router)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save file
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Generate label text (caption/transcription/filename fallback)
    text = await generate_label_text(file, filepath)

    # Generate embedding
    try:
        if MODE == "gemini":
            # Gemini can embed any file type
            embedding = get_embedding(filepath=filepath, mime_type=file.content_type)
        else:
            # OpenAI can only embed text
            embedding = get_embedding(text)
    except Exception as e:
        print(f"Embedding failed: {e}")
        return {"error": "embedding failed"}

    # Build item
    item = {
        "id": file_id,
        "filename": file.filename,
        "filepath": filepath,
        "embedding": embedding,
        "type": file.content_type,
        "text": text
    }

    # Update DB
    db.append(item)
    db_map[file_id] = item

    with open("db.json", "w") as f:
        json.dump(db, f)

    # Update FAISS
    build_index(db)

    return {"id": file_id}

async def generate_label_text(file: UploadFile, filepath: str) -> str:
    content_type = file.content_type

    # Audio transcription
    if "audio" in content_type:
        try:
            return transcribe_audio(filepath)
        except Exception as e:
            print(f"Transcription failed: {e}")
            return file.filename

    # Image caption
    if "image" in content_type:
        try:
            return describe_image(filepath)
        except Exception as e:
            print(f"Caption failed: {e}")
            return file.filename

    # Default filename
    return file.filename


@app.post("/search")
async def search(query: str = None, query_id: str = None):

    if query_id:
        query_item = db_map.get(query_id)
        if not query_item:
            return []

        query_emb = np.array(query_item["embedding"])

    else:
        try:
            query_emb = get_embedding(query)
        except Exception as e:
            print(f"embedding failed. Error: {e}")
            return []

    results_idx = faiss_search(query_emb, k=5)

    results = []
    for r in results_idx:
        item = db_map.get(r["id"])
        if item:
            results.append({
                "id": item["id"],
                "filename": item["filename"],
                "type": item["type"],
                "score": r["score"],
                "text": item.get("text", "")
            })

    return results


@app.get("/file/{file_id}")
def get_file(file_id: str):
    item = db_map.get(file_id)
    if item:
        return FileResponse(item["filepath"])

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/favicon.ico")
def favicon():
    return {}

@app.get("/health")
def health():
    return {"status": "healthy"}

# temp to assess models and methods
@app.get("/models")
def list_models():
    import google.genai as genai
    import os

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    models = client.models.list()

    return [
        {
            "name": m.name,
            "methods": m.supported_methods
        }
        for m in models
    ]

