"""Milestone 3 — run the whole ingestion + chunking pipeline in order.

Equivalent to running, from the project root:
    python -m src.ingest
    python -m src.clean
    python -m src.chunk
    python -m src.inspect_chunks 5

Usage:  python -m src.pipeline
"""

from __future__ import annotations

from . import chunk, clean, ingest, inspect_chunks


def main() -> None:
    print("\n=== 1/4  INGEST ===")
    ingest.main()
    print("\n=== 2/4  CLEAN ===")
    clean.main()
    print("\n=== 3/4  CHUNK ===")
    chunk.main()
    print("\n=== 4/4  INSPECT (5 representative chunks) ===")
    inspect_chunks.main()


if __name__ == "__main__":
    main()
