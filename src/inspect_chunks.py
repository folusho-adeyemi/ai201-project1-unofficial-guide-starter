"""Milestone 3 — inspection helper.

Prints the total chunk count and a set of representative chunks (evenly spaced
across the corpus) so you can sanity-check the chunking against the spec:
does each chunk stand on its own? Is it 400-600 words? Any HTML artifacts?

Usage:  python -m src.inspect_chunks [N]   (default N=5)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_FILE = PROJECT_ROOT / "documents" / "chunks" / "chunks.jsonl"


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    if not CHUNK_FILE.exists():
        print("No chunks found. Run `python -m src.chunk` first.")
        return

    chunks = [json.loads(line) for line in CHUNK_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    total = len(chunks)
    print(f"TOTAL CHUNKS: {total}\n")
    if total == 0:
        return

    # Evenly spaced sample across the corpus.
    step = max(1, total // n)
    sample = chunks[::step][:n]

    for c in sample:
        print("=" * 78)
        print(f"chunk_id={c['chunk_id']}  source={c['source_name']!r}  words={c['word_count']}")
        print("-" * 78)
        print(c["text"])
        print()


if __name__ == "__main__":
    main()
