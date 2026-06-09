"""Milestone 4 — shared vector-store + embedding-model helpers.

Centralizes the things embed.py and retrieve.py both need so they stay in sync:
the embedding model name, the ChromaDB location, the collection name, and a
lazily-loaded singleton SentenceTransformer (loading the model takes a second or
two, so we only do it once per process).
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "chroma_db"          # persistent on-disk store (gitignored)
COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"                   # per planning.md Retrieval Approach

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Return the embedding model, loading it once and caching it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(texts: list[str]):
    """Embed a list of texts. normalize_embeddings=True gives unit vectors so that
    ChromaDB's cosine distance behaves as 1 - cosine_similarity (0 = identical)."""
    return get_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )


def get_client() -> chromadb.api.ClientAPI:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    """Open the existing collection (created/populated by embed.py).

    We pin the distance metric to cosine via "hnsw:space" so distance scores are
    comparable to the 0.5 / 0.6-0.7 thresholds used when judging retrieval.
    """
    return get_client().get_collection(name=COLLECTION_NAME)
