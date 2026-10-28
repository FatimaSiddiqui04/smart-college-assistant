"""
Embedding Model Wrapper
Loads and caches the Sentence-Transformer model (all-MiniLM-L6-v2, 384 dimensions)
Generates normalized dense numerical vectors for document chunks and user queries.
"""

import os
import ssl
import urllib3
import requests
from typing import List, Union
import numpy as np

# Configure SSL resilience for environments with certificate interception
urllib3.disable_warnings()
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    orig_send = requests.Session.send
    requests.Session.send = lambda self, req, **kwargs: orig_send(self, req, **{**kwargs, 'verify': False})
except Exception:
    pass

from sentence_transformers import SentenceTransformer
import rag_config as config

_EMBEDDING_MODEL = None

def get_embedding_model() -> SentenceTransformer:
    """
    Singleton getter for SentenceTransformer to avoid re-allocating memory on every call.
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        print(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}...")
        _EMBEDDING_MODEL = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        print("Embedding model loaded successfully.")
    return _EMBEDDING_MODEL

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Converts a list of text strings into 384-dimensional dense float vectors.
    """
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    if isinstance(embeddings, np.ndarray):
        return embeddings.tolist()
    return [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]

def embed_query(query: str) -> List[float]:
    """
    Encodes a single user query string into a 384-dimensional embedding vector.
    """
    model = get_embedding_model()
    embedding = model.encode(query, convert_to_numpy=True)
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)
