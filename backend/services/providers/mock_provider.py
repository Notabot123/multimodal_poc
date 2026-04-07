import os
import numpy as np

import hashlib

def fake_embedding(text):
    # should be deterministic for a given input
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.random(384)
    return (vec / np.linalg.norm(vec)).tolist()

def fake_transcribe(filepath: str) -> str:
    # if no API service for demo
    filename = os.path.basename(filepath).lower()
        
    return f"audio recording of {filename}"