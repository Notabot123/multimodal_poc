import faiss
import numpy as np
import os

INDEX_FILE = "faiss.index"

index = None
id_map = []


def build_index(db, mode="exact"):
    global index, id_map    

    if not db:
        print("No db file to build FAISS index")
        return

    vectors = np.array([item["embedding"] for item in db]).astype("float32")

    dim = vectors.shape[1]

    if mode == "exact":
        # can take a bit longer on large datasets
        index = faiss.IndexFlatIP(dim)
    elif mode == "hnsw":
        # faster, more scalable but approx
        index = faiss.IndexHNSWFlat(dim, 32)

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
    
    k = min(k, len(id_map))

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