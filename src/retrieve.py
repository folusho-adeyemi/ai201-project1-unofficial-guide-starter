"""Milestone 4 — Stage 4: Retrieval.

`retrieve(query, k)` embeds the query with the same all-MiniLM-L6-v2 model used
for the chunks, runs a cosine-distance nearest-neighbor search over the ChromaDB
collection, and returns the top-k chunks with their source metadata and distance
scores (lower = closer; 0 = identical).

Run directly to smoke-test retrieval against the evaluation-plan questions from
planning.md:
    .venv/bin/python -m src.retrieve
"""

from __future__ import annotations

import textwrap

from .store import embed, get_collection

# The 5 evaluation questions from planning.md.
EVAL_QUERIES = [
    "Which neighborhoods do students most commonly recommend near Vanderbilt?",
    "What concerns do students mention about some apartment complexes?",
    "What tradeoff do students discuss when choosing housing?",
    "Where do students recommend finding roommates?",
    "Is living close to campus considered worth the cost?",
]


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k chunks most relevant to `query`, closest first."""
    query_embedding = embed([query])[0].tolist()
    collection = get_collection()
    res = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    results = []
    for rank, (doc, meta, dist) in enumerate(
        zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1
    ):
        results.append(
            {
                "rank": rank,
                "distance": dist,
                "source_name": meta.get("source_name", "?"),
                "source_url": meta.get("source_url", "?"),
                "chunk_index": meta.get("chunk_index"),
                "text": doc,
            }
        )
    return results


def _print_results(query: str, results: list[dict]) -> None:
    print("=" * 90)
    print(f"QUERY: {query}")
    print("=" * 90)
    for r in results:
        snippet = textwrap.shorten(r["text"].replace("\n", " "), width=260, placeholder=" ...")
        print(f"\n  #{r['rank']}  distance={r['distance']:.3f}  "
              f"source={r['source_name']!r}  (chunk {r['chunk_index']})")
        print(textwrap.fill(snippet, width=88, initial_indent="     ", subsequent_indent="     "))
    print()


def main(k: int = 5) -> None:
    for query in EVAL_QUERIES:
        _print_results(query, retrieve(query, k=k))


if __name__ == "__main__":
    main()
