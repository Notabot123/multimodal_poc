from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid, os, json
import numpy as np
from dotenv import load_dotenv

load_dotenv()
MODE = os.getenv("EMBEDDING_MODE", "mock")

from services.embedding import get_embedding
from services.providers.gemini_provider import get_embedding_from_file        
from services.speech import transcribe_audio
from services.caption import describe_image
from services.vector_store import build_index, load_index
from services.vector_store import search as faiss_search
from services.db import db
from api.visualise import router as visualise_router

app = FastAPI()

#  fast lookup map
db_map = {item["id"]: item for item in db}

#  load FAISS index if exists
load_index(db)
if not db:
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
    filepath = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # modality handling, used for labels only where gemini invoked
    if "audio" in file.content_type:
        try:
            text = transcribe_audio(filepath)
        except Exception as e:
            print(f"transcription failed: {e}")
            text = file.filename
    elif "image" in file.content_type:
        try:
            text = describe_image(filepath)
        except Exception as e:
            print(f"caption failed: {e}")
            text = file.filename
    else:
        text = file.filename

    # embedding
    try:       

        if MODE == "gemini":
            embedding = get_embedding_from_file(filepath, file.content_type)
        else:
            embedding = get_embedding(text)
    except Exception as e:
        print(f"embedding failed. Error: {e}")
        return {"error": "embedding failed"}

    item = {
        "id": file_id,
        "filename": file.filename,
        "filepath": filepath,
        "embedding": embedding,
        "type": file.content_type,
        "text": text
    }

    db.append(item)
    db_map[file_id] = item  #  update map

    # write db to file, until we transition to proper db
    with open("db.json", "w") as f:
        json.dump(db, f)

    # update FAISS index
    build_index(db)

    return {"id": file_id}


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