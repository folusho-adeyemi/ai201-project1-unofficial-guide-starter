"""Milestone 5 — Gradio interface for The Unofficial Guide.

A viewer can type a question about off-campus housing near Vanderbilt / Belmont /
TSU, and the app retrieves relevant chunks, generates a grounded answer, and
shows which source documents the answer drew from.

Run:  .venv/bin/python app.py
Then open http://localhost:7860
"""

from __future__ import annotations

import gradio as gr

from src.generate import ask

EXAMPLES = [
    "Which neighborhoods do students most commonly recommend near Vanderbilt?",
    "What concerns do students mention about The Broadview?",
    "Is living close to campus worth the cost?",
    "Where do students recommend finding roommates?",
    "What should I ask about before signing a lease?",
]


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    answer = result["answer"]
    if result["sources"]:
        sources = "\n".join(f"• {s}" for s in result["sources"])
    else:
        sources = "(no sources — the guide doesn't cover this)"
    return answer, sources


with gr.Blocks(title="The Unofficial Guide — Nashville Student Housing") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about **off-campus housing near Vanderbilt, Belmont, and Tennessee State.** "
        "Answers come *only* from real student discussions and housing guides — if the "
        "sources don't cover your question, the guide will say so."
    )
    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. Which neighborhoods do students recommend near Vanderbilt?",
            lines=2,
            scale=4,
        )
        btn = gr.Button("Ask", variant="primary", scale=1)

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from (sources)", lines=4)

    gr.Examples(examples=EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
