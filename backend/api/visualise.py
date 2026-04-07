from fastapi import APIRouter
import numpy as np
from sklearn.manifold import TSNE

router = APIRouter()

# IMPORTANT: we need access to mock db
# simplest approach for now:
from services.db import db


@router.get("/visualise")
def visualise():
    if len(db) < 2:
        return []

    try:
        embeddings = np.array([item["embedding"] for item in db])

        tsne = TSNE(
            n_components=2,
            perplexity=min(5, len(db) - 1),  # avoid errors on small sets
            random_state=42
        )

        coords = tsne.fit_transform(embeddings)

        results = []
        for i, item in enumerate(db):
            results.append({
                "id": item["id"],
                "filename": item["filename"],
                "type": item["type"],
                "x": float(coords[i][0]),
                "y": float(coords[i][1])
            })

        return results

    except Exception as e:
        print(f"t-SNE error: {e}")
        return []