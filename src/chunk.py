"""Milestone 3 — Stage 2b: Chunking.

Implements the Chunking Strategy from planning.md:
  - Target 400-600 words per chunk, with 75-100 words of overlap between
    adjacent chunks (we use 500-word target, 600 hard cap, ~90-word overlap).
  - Structure-aware: split on natural boundaries FIRST (Reddit -> per comment,
    web/articles -> per paragraph/section heading), then pack those segments up
    to the target so chunks stay close to a single topic.
  - Overlap carries the tail of one chunk into the next so context that sits on
    a boundary (e.g. a neighborhood named in one paragraph, its safety notes in
    the next) isn't lost at retrieval time.

Output: documents/chunks/chunks.jsonl  (one JSON object per chunk, with source
metadata for attribution downstream).

Usage:  python -m src.chunk
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = PROJECT_ROOT / "documents" / "clean"
CHUNK_DIR = PROJECT_ROOT / "documents" / "chunks"
CHUNK_FILE = CHUNK_DIR / "chunks.jsonl"

HEADER_SEP = "=" * 70

# Targets from planning.md's Chunking Strategy section.
TARGET_WORDS = 500   # aim for the middle of the 400-600 band
MAX_WORDS = 600      # hard cap
OVERLAP_WORDS = 90   # middle of the 75-100 band

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def parse_header(text: str) -> tuple[dict, str]:
    head, _, body = text.partition(HEADER_SEP)
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip().lower()] = v.strip()
    return meta, body.lstrip("\n")


def word_count(text: str) -> int:
    return len(text.split())


def segment(body: str, kind: str) -> list[str]:
    """Break a document into natural units before packing into chunks.

    Reddit: each comment / the post body is its own unit.
    Web/article: each paragraph (blank-line separated) is a unit; a heading
    line is glued to the paragraph that follows it so the section title travels
    with its content.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]

    if kind == "reddit":
        return paras

    # Web/article: attach short heading-like lines to the next paragraph.
    units: list[str] = []
    pending_heading = None
    for p in paras:
        is_heading = len(p.split()) <= 8 and not p.endswith((".", "!", "?", ":"))
        if is_heading:
            pending_heading = p
            continue
        if pending_heading:
            units.append(f"{pending_heading}\n{p}")
            pending_heading = None
        else:
            units.append(p)
    if pending_heading:
        units.append(pending_heading)
    return units


def split_long_unit(unit: str) -> list[str]:
    """Split a single oversized unit (> MAX_WORDS) on sentence boundaries."""
    sentences = SENTENCE_SPLIT.split(unit)
    pieces, current = [], []
    for s in sentences:
        current.append(s)
        if word_count(" ".join(current)) >= TARGET_WORDS:
            pieces.append(" ".join(current))
            current = []
    if current:
        pieces.append(" ".join(current))
    return pieces


def overlap_tail(text: str, min_words: int = 75, max_words: int = 100) -> str:
    """Return a sentence-aligned tail of `text` to seed the next chunk's overlap.

    We add whole sentences from the end until we have at least `min_words`
    (capped near `max_words`). Aligning to sentence boundaries keeps each new
    chunk starting on a clean, readable sentence rather than mid-phrase.
    """
    sentences = [s for s in SENTENCE_SPLIT.split(text.strip()) if s]
    tail: list[str] = []
    count = 0
    for s in reversed(sentences):
        tail.insert(0, s)
        count += word_count(s)
        if count >= min_words:
            break
    if not tail:
        return ""
    # If a single trailing sentence is huge, fall back to a word-count tail.
    if count > max_words and len(tail) == 1:
        words = tail[0].split()
        return " ".join(words[-max_words:])
    return " ".join(tail)


def pack(units: list[str]) -> list[str]:
    """Pack natural units into chunks of ~TARGET_WORDS with word overlap."""
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    def flush():
        nonlocal current, current_words
        if current:
            chunks.append("\n\n".join(current).strip())
            current, current_words = [], 0

    for unit in units:
        if word_count(unit) > MAX_WORDS:
            flush()
            for piece in split_long_unit(unit):
                chunks.append(piece.strip())
            # seed overlap from the last emitted piece
            if chunks:
                tail = overlap_tail(chunks[-1])
                if tail:
                    current, current_words = [tail], word_count(tail)
            continue

        # Would adding this unit blow the cap? Close the chunk first.
        if current_words + word_count(unit) > MAX_WORDS and current_words > 0:
            emitted = "\n\n".join(current).strip()
            chunks.append(emitted)
            tail = overlap_tail(emitted)
            current = [tail] if tail else []
            current_words = word_count(tail) if tail else 0

        current.append(unit)
        current_words += word_count(unit)

        if current_words >= TARGET_WORDS:
            emitted = "\n\n".join(current).strip()
            chunks.append(emitted)
            tail = overlap_tail(emitted)
            current = [tail] if tail else []
            current_words = word_count(tail) if tail else 0

    # Flush remainder, but avoid emitting a chunk that's only the carried tail.
    if current:
        remainder = "\n\n".join(current).strip()
        if chunks and remainder == overlap_tail(chunks[-1]):
            pass  # nothing new beyond the overlap; drop it
        else:
            chunks.append(remainder)
    return chunks


def main() -> None:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    clean_files = sorted(CLEAN_DIR.glob("*.txt"))
    if not clean_files:
        print("No clean files found. Run `python -m src.clean` first.")
        return

    all_chunks = []
    per_source_counts = []
    for path in clean_files:
        meta, body = parse_header(path.read_text(encoding="utf-8"))
        kind = meta.get("source_kind", "web")
        if word_count(body) < 30:
            per_source_counts.append((meta.get("source_name", path.name), 0))
            continue
        units = segment(body, kind)
        chunks = pack(units)
        for i, text in enumerate(chunks):
            all_chunks.append(
                {
                    "chunk_id": f"{meta.get('source_id', '?')}-{i:03d}",
                    "source_id": meta.get("source_id", "?"),
                    "source_name": meta.get("source_name", "?"),
                    "source_url": meta.get("source_url", "?"),
                    "word_count": word_count(text),
                    "text": text,
                }
            )
        per_source_counts.append((meta.get("source_name", path.name), len(chunks)))

    with CHUNK_FILE.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print("Chunks per source:")
    for name, n in per_source_counts:
        print(f"  {n:4d}  {name}")
    total = len(all_chunks)
    print(f"\nTOTAL CHUNKS: {total}  -> {CHUNK_FILE.relative_to(PROJECT_ROOT)}")
    if total:
        sizes = [c["word_count"] for c in all_chunks]
        print(f"Word count per chunk: min {min(sizes)}, max {max(sizes)}, "
              f"avg {sum(sizes) // len(sizes)}")
    if total < 50:
        print("NOTE: fewer than 50 chunks across the corpus — see report on "
              "blocked sources before judging chunk size.")
    elif total > 2000:
        print("NOTE: more than 2,000 chunks — chunks may be too small.")


if __name__ == "__main__":
    main()
