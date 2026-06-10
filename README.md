# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Off-campus housing around Nashville universities — primarily **Vanderbilt**, with **Belmont**
and **Tennessee State** coverage. The system answers questions about which neighborhoods and
apartment complexes students recommend, safety, commute, pricing, lease pitfalls, and roommate
experiences.

This knowledge is valuable because official channels (university housing portals, apartment
listings) publish rent, amenities, and lease terms but almost never the lived experience:
maintenance problems, mold, noise, management responsiveness, whether a building is worth its
price, or how the off-campus authorization process actually plays out. Students get that
information instead from Reddit threads, student-newspaper articles, and neighborhood guides —
scattered, unindexed, and easy to miss. This RAG system consolidates those real student voices
into one queryable, source-cited assistant.

---

## Document Sources

The corpus is defined in `src/sources.py`. It grew from the 10 sources in `planning.md` to 21:
the original Reddit threads turned out to be short (4–8 comments each), so I added
neighborhood/cost guides covering all three schools to build a corpus that supports precise
retrieval. **18 of 21 sources loaded successfully → 50 chunks.** (Reddit and the official portals
aggressively bot-block automated requests; the Reddit threads were captured via the browser and
loaded through a manual-file fallback in `src/ingest.py`.)

| # | Source | Type | URL or file path | Loaded? |
|---|--------|------|-----------------|---------|
| 1 | Vanderbilt Housing Discussion | Reddit | reddit.com/r/Vanderbilt/comments/1r39b3j | ✅ (manual) |
| 2 | Off-Campus Housing Culture Question | Reddit | reddit.com/r/Vanderbilt/comments/1pgpkql | ✅ (manual) |
| 3 | Transfer Student Housing Thread | Reddit | reddit.com/r/Vanderbilt/comments/1lbtw3s | ✅ (manual) |
| 4 | Off-Campus Housing and Roommates | Reddit | reddit.com/r/Vanderbilt/comments/hcsa2x | ❌ not saved |
| 5 | Housing Recommendations | Reddit | reddit.com/r/Vanderbilt/comments/1krbrap | ✅ (manual) |
| 6 | Graduate Student Housing Recommendations | Reddit | reddit.com/r/Vanderbilt/comments/1kh1ywm | ✅ (manual) |
| 7 | Broadview vs On-Campus Housing | Reddit | reddit.com/r/Vanderbilt/comments/1kdkode | ✅ (manual) |
| 8 | Student Housing in Nashville Guide | Web (SPA) | thestudentsublet.com/blog/student-housing-nashville-guide | ❌ JS-rendered |
| 9 | What I Learned From My Off-Campus Apartment Hunt | Article | vanderbilthustler.com/2025/04/13/... | ✅ |
| 10 | Vanderbilt Off-Campus Housing Portal | Portal | offcampushousing.vanderbilt.edu | ❌ bot-blocked |
| 11 | Prked Vanderbilt Off-Campus Housing Guide | Web guide | prked.com/post/vanderbilt-off-campus-housing-guide | ✅ |
| 12 | 8 Best Nashville Neighborhoods Near Vanderbilt | Web guide | nashvillesmls.com/blog/best-neighborhoods-near-vanderbilt-nashville-tn.html | ✅ |
| 13 | Where Should I Live Off Campus? | Article | vanderbilthustler.com/2026/02/13/where-should-i-live-off-campus | ✅ |
| 14 | 8 Best Neighborhoods Near Belmont University | Web guide | nashvillesmls.com/blog/best-neighborhoods-near-belmont-university.html | ✅ |
| 15 | How Much Does It Cost to Live in Nashville | Web guide | rentwithzachandkayla.com/blog/...nashville-apartment-in-2026 | ✅ |
| 16 | Moving to Nashville: Neighborhood Guide | Web guide | househavenrealty.com/blog/moving-to-nashville-2026 | ✅ |
| 17 | Nashville Neighborhoods for Relocators | Web guide | dwalshhomes.com/blog/best-nashville-neighborhoods-for-relocating-professionals | ✅ |
| 18 | Moving to Nashville Guide (Nashville Guru) | Web guide | nashvilleguru.com/2071/moving-to-nashville-guide | ✅ |
| 19 | Apartments Near Belmont University (AptAmigo) | Web guide | aptamigo.com/TN/Nashville/Apartments/apartments-near-belmont-university-nashville | ✅ |
| 20 | Apartments Near Tennessee State University (Amber) | Web guide | amberstudent.com/places/search/tennessee-state-university-2410078108302 | ✅ |
| 21 | TSU Alternate (Off-Campus) Housing Options | Portal/guide | tnstate.edu/housing/alternatehousing.aspx | ✅ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400–600 words (target 500, hard cap 600), implemented in `src/chunk.py`.

**Overlap:** 75–100 words, sentence-aligned (the tail of each chunk is carried into the next,
snapped to a sentence boundary so chunks start cleanly).

**Why these choices fit your documents:** The corpus is opinion-heavy and structurally varied, so
chunking is **structure-aware first, then size-packed**. Natural units are extracted before
packing: Reddit threads split per comment (the post + each comment is a unit, with `u/author`
attribution preserved), and web guides/articles split per paragraph with short heading lines glued
to the section they introduce. Those units are packed to ~500 words so each chunk is one coherent
topic (e.g. a single neighborhood's vibe + commute + downside). Overlap matters here because
context often straddles a boundary — one paragraph names a neighborhood, the next gives its safety
or price note — and 75–100 words is enough to carry that bridge without duplicating whole topics.

Preprocessing before chunking (`src/clean.py`): strip HTML tags, isolate the main content
container, remove nav/header/footer/cookie/share/ad **and reader-comment** sections, unescape HTML
entities (`&amp;`, `&nbsp;`), and collapse whitespace. Stripping comment sections was important —
one general "moving to Nashville" guide had a 72k-character reader-comment thread (single moms,
touring musicians) that would have diluted the student-housing corpus with off-topic chunks.

**Final chunk count:** **50** chunks across 18 loaded sources (min 91, max 599, avg ~456 words).
This sits in the healthy 50–2,000 range for ~10–20 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (`src/store.py`). Embeddings are
L2-normalized and stored in a persistent ChromaDB collection configured for cosine distance
(`metadata={"hnsw:space": "cosine"}`), so distance scores read as `1 − cosine_similarity`
(0 = identical). I chose it because it runs locally with no API key or rate limits, is small/fast
(384-dim), and performs well on the short, opinion-style English text in this corpus. Retrieval is
top-k = 5.

**Production tradeoff reflection:** If cost weren't a constraint, I'd weigh:
- **Accuracy on domain text:** a larger model (`BAAI/bge-large-en-v1.5`, OpenAI
  `text-embedding-3-large`) would better separate near-duplicate housing chunks — e.g.
  distinguishing "finding roommates" from "finding an apartment," where MiniLM's 384-dim vectors
  topped out at distance 0.46 and the model conflated the two (see Failure Case below).
- **Context length:** MiniLM truncates at ~256 tokens (~200 words), shorter than my 400–600-word
  chunks, so each chunk's tail isn't embedded. An 8k-token model would embed whole chunks and let
  me use larger chunks without losing signal.
- **Latency & ops:** local MiniLM is ~10ms/query with zero network; an API model adds round-trip
  latency, a per-call bill, and rate limits, but removes self-hosting.
- **Multilingual:** not needed here (English corpus), but would matter for international-student
  sources.
For a free, local, low-latency student project, MiniLM is the right tradeoff — retrieval is
already on-topic with top distances of 0.28–0.46.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The system prompt (`src/generate.py`, `SYSTEM_PROMPT`) *enforces* grounding rather than
suggesting it. It tells `llama-3.3-70b-versatile`: "Answer using ONLY the information in the
CONTEXT documents... Do NOT use any outside or prior knowledge," and "If the CONTEXT does not
contain enough information to answer, reply with EXACTLY this sentence and nothing else: 'I don't
have enough information on that.'" It also forbids inventing apartment names, prices, or sources,
and requires citing the bracketed `[Source N]` label for each fact. Generation runs at
`temperature=0.1` to keep the model close to the retrieved text.

Two structural choices back up the prompt:
1. **Distance gate (pre-LLM):** before calling the model, `ask()` checks the closest chunk's
   cosine distance. If it exceeds `NO_MATCH_DISTANCE = 0.75`, the system returns the "not enough
   information" message *without* an LLM call — so a question the corpus doesn't cover (e.g. "What
   is the best pizza topping?") can't be answered from training knowledge at all.
2. **Numbered, labeled context:** retrieved chunks are passed as `[Source N] <name>` blocks, so
   the model's inline citations map to real documents.

**How source attribution is surfaced in the response:**
Attribution is guaranteed programmatically, not left to the LLM. After generation, `ask()`
returns a `sources` list built from the retrieved chunks' stored metadata (`source_name`), in
rank order, deduplicated. The Gradio UI (`app.py`) displays this list in a separate
"Retrieved from (sources)" box beneath the answer. The model is *also* asked to cite `[Source N]`
inline, but even if it forgot, the source list still appears. When the system declines (no good
match), the source list is empty.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

Run with `.venv/bin/python -m src.generate` (or through the Gradio UI). Distances are the top-1
cosine score for each query.

| # | Question | Expected answer | System response (summarized) | Top distance | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|--------------|-------------------|-------------------|
| 1 | Which neighborhoods do students most commonly recommend near Vanderbilt? | Hillsboro Village, Midtown, Belmont-Hillsboro appear frequently | Hillsboro Village, Elliston Place, Midtown, the Gulch, West End, 12 South, Sylvan Park; noted safety caveats — all cited to [Source N] | 0.283 | Relevant | **Accurate** |
| 2 | What concerns do students mention about some apartment complexes? | Maintenance issues, mold complaints, management responsiveness | The Broadview's high cost/sq-ft, a mold problem that made a student sick, a lawsuit against the builder, and 60-day-notice lease traps | 0.420 | Relevant | **Accurate** (mold + cost + lease; "management responsiveness" not surfaced) |
| 3 | What tradeoff do students discuss when choosing housing? | Convenience versus rent cost | Framed mostly as on-campus (community/integration) vs off-campus (better facilities, but mold risk, cooking, longer walk) | 0.405 | Relevant | **Partially accurate** (real tradeoff, but drifted from convenience-vs-cost) |
| 4 | Where do students recommend finding roommates? | Housing groups, Reddit, university communities | Transfer-student/Discord groups and talking to current students — but also suggested Apartments.com/Zillow, which the source mentions for finding *apartments*, not roommates | 0.461 | Partially relevant | **Partially accurate** (see Failure Case) |
| 5 | Is living close to campus considered worth the cost? | Many say convenience is valuable but expensive | Convenient but pricey (Broadview <3-min walk yet higher $/sq-ft); pulled in some TSU/Belmont rent figures for a Vanderbilt-framed question | 0.345 | Relevant | **Partially accurate** (core right; mixed in cross-school rent numbers) |

**Overall:** 2 Accurate, 3 Partially accurate, 0 Inaccurate. Retrieval is relevant on 4/5 (top
distances 0.28–0.46, all under the 0.5 checkpoint); the roommate query is the consistent weak
spot.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Where do students recommend finding roommates?" (Q4) — partially
accurate, and the weakest query in the eval set.

**What the system returned:** It correctly surfaced one real recommendation — using transfer-student
/ Discord groups and talking to current students — but then added that students "can use online
platforms like Apartments.com and Zillow to find places and potentially connect with roommates."
That last clause is a stretch: the cited source (Prked guide) mentions Apartments.com/Zillow for
finding *apartments*, not roommates. The answer blends a genuine answer with an adjacent-but-wrong
one.

**Root cause (tied to a specific pipeline stage):** This is primarily an **ingestion / corpus-coverage**
failure that surfaces at **retrieval**, then gets amplified at **generation**. My corpus barely
covers roommate-finding — essentially one Reddit comment ("try a transfer student group, is there a
discord… see if anyone else is willing to share a house or apt"). So the embedding search has no
strong signal to match: the top-1 cosine distance is 0.461, noticeably higher than the 0.28–0.42 of
the other queries, and the retrieved chunks are *about housing recommendations generally* rather than
roommate-finding specifically. At generation time, the grounding prompt keeps the model inside the
retrieved text, but because that text is thin on the actual question, the model latches onto the
nearest adjacent fact (apartment-search sites) and over-extends it to "connect with roommates." The
distance gate (0.75) didn't trigger because 0.461 still looks "relevant" — it's a weak-but-not-absent
match, the hardest case to handle.

**What you would change to fix it:** (1) **Fix the root cause in ingestion** — add sources that
actually discuss roommate-finding (e.g. r/Vanderbilt/r/nashville roommate threads, the Belmont/TSU
roommate-matching marketplaces), so retrieval has real signal. (2) **Tighten the relevance gate per
intent** — a 0.46 top distance with no chunk below ~0.4 could trigger a softer "the guide only
touches on this briefly" hedge instead of a confident list. (3) **Prompt tweak-context handling** —
instruct the model that when context only partially addresses the question, it should answer the
covered part and explicitly say the rest isn't in the sources, rather than reaching for adjacent
facts.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The Chunking Strategy and Architecture
sections of `planning.md` gave me concrete, testable targets — 400–600 words, 75–100-word overlap,
"Reddit → chunk by comment, guides → chunk by section" — that I could hand almost verbatim to the AI
as an implementation brief. Because the numbers were specific, I could verify the generated chunker
against them objectively (printing chunk word counts and the total), and the labeled pipeline diagram
let the AI wire each stage to the right library (sentence-transformers → ChromaDB → Groq) without me
re-explaining the architecture each time. The spec turned "build a RAG system" into a checklist I
could grade myself against.

**One way your implementation diverged from the spec, and why:** The plan assumed ~10 sources, mostly
Reddit, chunked per comment. In practice the chosen Reddit threads were tiny (4–8 comments → ~9 chunks
total) and Reddit, the SPA guide, and the official portals all bot-blocked automated requests. To get
a meaningful, on-topic corpus I diverged in three ways the plan didn't anticipate: (1) I expanded to
21 sources, adding Belmont- and TSU-area neighborhood/cost guides — which also broadened the domain
beyond Vanderbilt; (2) I added a **manual-file fallback** ingester so browser-saved Reddit JSON could
be loaded past the bot-block; and (3) I added a reader-**comment-stripping** step in cleaning and a
**cosine-distance gate** before generation (for grounding) — neither was in the original plan. I
updated `planning.md`'s Documents and Retrieval sections to record these changes.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Ingestion + cleaning + chunking**

- *What I gave the AI:* My `planning.md` Documents table, the Chunking Strategy section (400–600
  words, 75–100 overlap, per-source structure), and the pipeline diagram, with a request to
  implement `ingest.py`, `clean.py`, and `chunk.py`.
- *What it produced:* A working three-stage pipeline (Reddit `.json` ingestion, BeautifulSoup
  cleaning, structure-aware chunking). But the cleaner was too aggressive: its boilerplate filter
  matched the substring "sidebar" inside the Hustler article's wrapper class
  (`sno-story-sidebar-mode-single`) and deleted the entire article body, producing 0 words.
- *What I changed or overrode:* I directed it to add a text-size guard (only remove a
  boilerplate-looking element if it holds <400 chars) and to split the rules into "always remove"
  (comments, cookie, share, ads — regardless of size) vs "remove only if small" (ambiguous tokens
  like `sidebar`). I also had it add reader-**comment-section** stripping after I inspected the
  chunks and found a 72k-char comment thread diluting the corpus with off-topic relocation Q&A.

**Instance 2 — Embedding, retrieval, and grounded generation**

- *What I gave the AI:* My Retrieval Approach section (all-MiniLM-L6-v2, top-k 5) plus the explicit
  grounding requirement (answer from retrieved context only, with source attribution) and the
  Gradio skeleton.
- *What it produced:* `embed.py`/`retrieve.py`/`generate.py` and a Gradio app. The first version
  enforced grounding through the system prompt and asked the LLM to cite its sources inline.
- *What I changed or overrode:* I overrode the attribution design — instead of trusting the LLM to
  cite, I made `ask()` build the source list **programmatically** from each retrieved chunk's stored
  metadata, so attribution is guaranteed even if the model forgets. I also added a **pre-LLM
  cosine-distance gate** (decline when the closest chunk is >0.75) so out-of-scope questions are
  refused without a model call, and set `temperature=0.1` to keep generation close to context.
