import faiss
import numpy as np
import os

INDEX_FILE = "faiss.index"

index = None
id_map = []


def build_index(db):
    global index, id_map

    if not db:
        return

    vectors = np.array([item["embedding"] for item in db]).astype("float32")

    dim = vectors.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    id_map = [item["id"] for item in db]

    # persist index
    faiss.write_index(index, INDEX_FILE)


def load_index(db):
    global index, id_map

    if os.path.exists(INDEX_FILE):
        index = faiss.read_index(INDEX_FILE)
        id_map = [item["id"] for item in db]


def search(query_vector, k=5):
    if index is None:
        return []

    query_vector = np.array([query_vector]).astype("float32")

    scores, indices = index.search(query_vector, k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(id_map):
            results.append({
                "id": id_map[idx],
                "score": float(scores[0][i])
            })

    return results