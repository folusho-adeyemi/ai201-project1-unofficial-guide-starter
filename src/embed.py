"""Milestone 4 — Stage 3: Embedding + vector store.

Loads the chunks produced by the ingestion/chunking pipeline
(documents/chunks/chunks.jsonl), embeds each with all-MiniLM-L6-v2, and stores
them in a persistent ChromaDB collection together with source metadata
(source name, source URL, and the chunk's position in its document) so we can
attribute answers later.

The collection is rebuilt from scratch each run (drop + recreate) so re-running
never produces duplicate vectors.

Usage:  .venv/bin/python -m src.embed
"""

from __future__ import annotations

import json
from pathlib import Path

from .store import (
    COLLECTION_NAME,
    MODEL_NAME,
    embed,
    get_client,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_FILE = PROJECT_ROOT / "documents" / "chunks" / "chunks.jsonl"
BATCH = 64


def load_chunks() -> list[dict]:
    if not CHUNK_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNK_FILE} not found — run the ingestion pipeline (python -m src.chunk) first."
        )
    return [
        json.loads(line)
        for line in CHUNK_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from {CHUNK_FILE.relative_to(PROJECT_ROOT)}")

    client = get_client()
    # Drop any previous version so re-running is idempotent.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine distance: 0 = identical
    )

    print(f"Embedding with {MODEL_NAME} and adding to collection '{COLLECTION_NAME}'...")
    for start in range(0, len(chunks), BATCH):
        batch = chunks[start : start + BATCH]
        texts = [c["text"] for c in batch]
        embeddings = embed(texts)
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            documents=texts,
            embeddings=[e.tolist() for e in embeddings],
            metadatas=[
                {
                    "source_id": str(c["source_id"]),
                    "source_name": c["source_name"],
                    "source_url": c["source_url"],
                    # chunk_id is "<source_id>-<index>"; index = position in that doc
                    "chunk_index": int(c["chunk_id"].split("-")[-1]),
                    "word_count": c["word_count"],
                }
                for c in batch
            ],
        )
        print(f"  added {min(start + BATCH, len(chunks))}/{len(chunks)}")

    print(f"\nDone. Collection now holds {collection.count()} vectors at "
          f"{(PROJECT_ROOT / 'chroma_db').relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
