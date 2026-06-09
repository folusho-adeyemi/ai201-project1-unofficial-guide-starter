"""Milestone 5 — Stage 5: Grounded generation.

`ask(question)` ties the pipeline together:
  1. retrieve the top-k chunks from ChromaDB (Milestone 4),
  2. if nothing is close enough (cosine distance gate), decline WITHOUT calling
     the LLM — this stops the model from answering off-topic questions from its
     training data,
  3. otherwise build a context block from the retrieved chunks and call Groq's
     llama-3.3-70b-versatile with a system prompt that *enforces* answering from
     context only,
  4. return the answer plus a source list that is built PROGRAMMATICALLY from the
     retrieved chunks' metadata — attribution does not depend on the LLM
     remembering to cite.

Usage:  .venv/bin/python -m src.generate
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from .retrieve import retrieve

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5
# Cosine distance above which we treat the corpus as having NO real match.
# Relevant results in testing scored 0.28-0.50; clearly off-topic queries land
# well above this, so we decline before spending an LLM call.
NO_MATCH_DISTANCE = 0.75
NOT_ENOUGH_INFO = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a retrieval-grounded assistant that answers "
    "questions about off-campus student housing near Nashville universities "
    "(Vanderbilt, Belmont, Tennessee State).\n\n"
    "STRICT RULES:\n"
    "1. Answer using ONLY the information in the CONTEXT documents provided in the "
    "user message. Do NOT use any outside or prior knowledge.\n"
    f"2. If the CONTEXT does not contain enough information to answer, reply with "
    f"EXACTLY this sentence and nothing else: \"{NOT_ENOUGH_INFO}\"\n"
    "3. Do not invent apartment names, prices, sources, or facts that are not in "
    "the CONTEXT.\n"
    "4. When you state a fact, cite the source it came from using the bracketed "
    "label shown in the CONTEXT (e.g. [Source 2]).\n"
    "5. Keep the answer concise and specific to what students actually said."
)


def _build_context(chunks: list[dict]) -> str:
    """Render retrieved chunks into a numbered CONTEXT block the model can cite."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(
            f"[Source {i}] {c['source_name']}\n{c['text']}"
        )
    return "\n\n---\n\n".join(blocks)


def _client() -> Groq:
    key = os.environ.get("GROQ_API_KEY")
    if not key or key == "your_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key "
            "(get a free one at https://console.groq.com)."
        )
    return Groq(api_key=key)


def ask(question: str, k: int = TOP_K) -> dict:
    """Return {"answer", "sources", "chunks"} for a question, grounded in the corpus."""
    chunks = retrieve(question, k=k)

    # Distance gate: if even the closest chunk is far, the corpus has no answer.
    if not chunks or chunks[0]["distance"] > NO_MATCH_DISTANCE:
        return {"answer": NOT_ENOUGH_INFO, "sources": [], "chunks": chunks}

    context = _build_context(chunks)
    user_message = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the CONTEXT above, and cite sources by their [Source N] label."
    )

    resp = _client().chat.completions.create(
        model=MODEL,
        temperature=0.1,  # low temperature keeps the model close to the context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    answer = resp.choices[0].message.content.strip()

    # Programmatic attribution: unique sources actually retrieved, in rank order.
    # If the model declined, surface no sources (nothing was used).
    sources: list[str] = []
    if answer != NOT_ENOUGH_INFO:
        seen = set()
        for c in chunks:
            label = c["source_name"]
            if label not in seen:
                seen.add(label)
                sources.append(label)

    return {"answer": answer, "sources": sources, "chunks": chunks}


def main() -> None:
    tests = [
        "Which neighborhoods do students most commonly recommend near Vanderbilt?",
        "What concerns do students mention about some apartment complexes?",
        "Is living close to campus considered worth the cost?",
        # Out-of-scope: our corpus has nothing on this; system should decline.
        "What is the best pizza topping?",
    ]
    for q in tests:
        result = ask(q)
        print("=" * 90)
        print(f"Q: {q}")
        print("-" * 90)
        print(result["answer"])
        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                print(f"  • {s}")
        print()


if __name__ == "__main__":
    main()
