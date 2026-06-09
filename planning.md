# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose the domain of off-campus housing around Nashville universities, particularly Vanderbilt University, Belmont University, and Tennessee State University. This knowledge is valuable because students often need information about apartment quality, neighborhood safety, landlord responsiveness, transportation, roommate experiences, and hidden rental costs before signing a lease.

Official university housing websites and apartment listings provide factual information such as rent prices, amenities, and lease terms, but they rarely include real student experiences. Students instead rely on Reddit discussions, housing forums, apartment reviews, student newspapers, and community recommendations to learn about issues such as maintenance problems, mold concerns, noise levels, commute difficulties, and whether a property is actually worth its price.

Sources include Reddit discussions, student newspaper articles, housing guides, apartment listings, and university housing resources.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #  | Source                                            | Description                                                                             | URL or Location                                                                            |
| -- | ------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1  | Vanderbilt Housing Discussion (Reddit)            | Student discussion about housing options and experiences near Vanderbilt University.    | https://www.reddit.com/r/Vanderbilt/comments/1r39b3j/housing/                              |
| 2  | Off-Campus Housing Culture Question (Reddit)      | Discussion about off-campus housing culture, expectations, and student experiences.     | https://www.reddit.com/r/Vanderbilt/comments/1pgpkql/offcampus_housing_culture_question/   |
| 3  | Transfer Student Housing Thread (Reddit)          | Advice and recommendations for transfer students seeking housing.                       | https://www.reddit.com/r/Vanderbilt/comments/1lbtw3s                                       |
| 4  | Off-Campus Housing and Roommates (Reddit)         | Student experiences finding roommates and housing near campus.                          | https://www.reddit.com/r/Vanderbilt/comments/hcsa2x                                        |
| 5  | Housing Recommendations (Reddit)                  | Recommendations and warnings regarding apartment complexes and neighborhoods.           | https://www.reddit.com/r/Vanderbilt/comments/1krbrap                                       |
| 6  | Graduate Student Housing Recommendations (Reddit) | Housing advice specifically targeted toward graduate students.                          | https://www.reddit.com/r/Vanderbilt/comments/1kh1ywm                                       |
| 7  | Broadview vs On-Campus Housing (Reddit)           | Comparison of off-campus and on-campus housing options.                                 | https://www.reddit.com/r/Vanderbilt/comments/1kdkode                                       |
| 8  | Student Housing in Nashville Guide                | Guide covering neighborhoods, pricing, and student housing considerations in Nashville. | https://thestudentsublet.com/blog/student-housing-nashville-guide                          |
| 9  | What I Learned From My Off-Campus Apartment Hunt  | Student newspaper article describing the apartment search process and lessons learned.  | https://vanderbilthustler.com/2025/04/13/what-i-learned-from-my-off-campus-apartment-hunt/ |
| 10 | Vanderbilt Off-Campus Housing Portal              | Official housing listing portal containing apartment listings and property information. | https://offcampushousing.vanderbilt.edu/                                                   |
| 11 | Prked Vanderbilt Off-Campus Housing Guide         | Neighborhood-by-neighborhood guide (Hillsboro Village, Midtown, Elliston, Gulch) with pros/cons. | https://prked.com/post/vanderbilt-off-campus-housing-guide                          |
| 12 | 8 Best Nashville Neighborhoods Near Vanderbilt    | Detailed breakdown of 8 neighborhoods near campus: amenities, vibe, pricing, commute.   | https://www.nashvillesmls.com/blog/best-neighborhoods-near-vanderbilt-nashville-tn.html    |
| 13 | Where Should I Live Off Campus? (Vanderbilt Hustler) | Student-written guide reviewing specific apartment buildings near campus with pros/cons. | https://vanderbilthustler.com/2026/02/13/where-should-i-live-off-campus/                 |
| 14 | 8 Best Neighborhoods Near Belmont University      | Neighborhood guide for Belmont students (Belmont/Hillsboro, 12 South, Edgehill, Melrose). | https://www.nashvillesmls.com/blog/best-neighborhoods-near-belmont-university.html        |
| 15 | How Much Does It Cost to Live in Nashville        | Relocator rent-cost guide: realistic studio/1BR/2BR ranges by neighborhood tier.        | https://rentwithzachandkayla.com/blog/how-much-does-it-really-cost-to-move-into-a-nashville-apartment-in-2026 |
| 16 | Moving to Nashville: Neighborhood Guide           | Honest neighborhood-by-neighborhood tradeoffs (East Nashville, 12 South, Sylvan Park).  | https://www.househavenrealty.com/blog/moving-to-nashville-2026                            |
| 17 | Nashville Neighborhoods for Relocators            | Compares core neighborhoods by commute, lifestyle, housing type, and budget.            | https://dwalshhomes.com/blog/best-nashville-neighborhoods-for-relocating-professionals    |
| 18 | Moving to Nashville Guide (Nashville Guru)        | Long-form guide covering Gulch, West End, Midtown, Hillsboro, Sylvan Park, and more.    | https://nashvilleguru.com/2071/moving-to-nashville-guide                                  |
| 19 | Apartments Near Belmont University (AptAmigo)     | Apartment pricing and recommended neighborhoods near Belmont University.                | https://www.aptamigo.com/TN/Nashville/Apartments/apartments-near-belmont-university-nashville |
| 20 | Apartments Near Tennessee State University (Amber) | Student apartment options and neighborhoods (Jefferson St, West End, Midtown) near TSU. | https://amberstudent.com/places/search/tennessee-state-university-2410078108302           |
| 21 | TSU Alternate (Off-Campus) Housing Options        | Official TSU guidance on off-campus housing, target zip codes, and search resources.    | https://www.tnstate.edu/housing/alternatehousing.aspx                                     |

> Sources 11–21 were added during Milestone 3: the originally chosen Reddit threads turned out
> to be short (4–8 comments each), so the corpus needed more substantive, neighborhood-level
> content to support precise retrieval. These guides auto-fetch (server-rendered HTML) and
> broaden coverage across all three target schools (Vanderbilt, Belmont, TSU) plus rent costs
> and commute/lifestyle tradeoffs. The cleaner strips reader-comment sections so general
> relocation Q&A doesn't dilute the student-housing corpus.


---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

I plan to chunk documents primarily by section or logical topic rather than using a strict fixed character count. Reddit threads naturally break into individual posts and comment chains, while housing guides and articles are organized into sections about neighborhoods, apartment complexes, transportation, pricing, or housing advice.

For implementation, I will use chunks of approximately 400–600 words with an overlap of 75–100 words between adjacent chunks.

The overlap is important because important information may appear near the boundary between two chunks. For example, one paragraph may describe a neighborhood while the next paragraph explains safety concerns. Without overlap, retrieval could miss part of the context.

Different document types will be chunked differently:

* Reddit threads: chunk by comment or small comment groups.
* Housing guides: chunk by section headings.
* Student articles: chunk by subsection or 2–3 paragraphs.
* Apartment listings: one property per chunk.

I chose this approach because most of the corpus consists of opinion-based text. Chunks that are too small may lose important context and make answers incomplete. Chunks that are too large may contain multiple unrelated topics, reducing retrieval accuracy.

Signs that chunks are too small:

* Answers lack context.
* Retrieval returns isolated sentences.
* The system misses supporting evidence.

Signs that chunks are too large:

* Retrieved chunks discuss several unrelated apartments or neighborhoods.
* The LLM receives unnecessary information.
* Retrieval becomes less precise.

Section-based chunking preserves natural document structure and typically produces more meaningful retrieval results than splitting strictly by character count.


---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** 
all-MiniLM-L6-v2 (via sentence-transformers). Embeddings are normalized to unit length and
stored in a persistent ChromaDB collection configured for cosine distance. Chosen because it
runs locally with no API key or rate limits, is small/fast (384-dim), and performs well on
short, opinion-style English text like Reddit comments and housing-guide paragraphs.

**Top-k:** 5

**Production tradeoff reflection:**
If cost weren't a constraint and this served real users, I'd weigh:
- **Accuracy on domain text:** a larger model (e.g. `BAAI/bge-large-en-v1.5` or OpenAI
  `text-embedding-3-large`) would better distinguish near-duplicate housing chunks — e.g.
  separating "rent vs. convenience" from "maintenance complaints" — where MiniLM's 384-dim
  vectors sometimes return topically-adjacent-but-not-exact results (my "finding roommates"
  query topped out at distance 0.46 rather than <0.3).
- **Context length:** MiniLM truncates at 256 tokens (~200 words), shorter than my 400–600-word
  chunks, so the tail of each chunk isn't embedded. A long-context model (8k tokens) would embed
  whole chunks and could let me use larger chunks without losing signal.
- **Latency & ops:** local MiniLM is ~10ms/query with zero network; an API model adds round-trip
  latency, a per-call bill, and a rate limit, but removes the need to host the model.
- **Multilingual:** not needed here (corpus is English), but a multilingual model (e.g.
  `paraphrase-multilingual-MiniLM`) would matter if I expanded to international-student sources.
For this project the local MiniLM tradeoff is the right one: retrieval is already on-topic with
top distances of 0.28–0.46, well under the 0.5 checkpoint threshold.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which neighborhoods do students most commonly recommend near Vanderbilt?|Hillsboro Village, Midtown, Belmont-Hillsboro appear frequently. |
| 2 | What concerns do students mention about some apartment complexes?| Maintenance issues, mold complaints, responsiveness of management.|
| 3 | What tradeoff do students discuss when choosing housing?| Convenience versus rent cost.|
| 4 | Where do students recommend finding roommates?| Housing groups, Reddit, university communities.|
| 5 | Is living close to campus considered worth the cost?| Many students say convenience is valuable but expensive.|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Noisy Data
Reddit comments may contain jokes, sarcasm, or inaccurate information.
2. Conflicting Opinions
Different students may have opposite experiences with the same apartment.
3. Off-topic Retrieval
A query about safety might retrieve chunks discussing rent prices.
4. Source Attribution
Ensuring every generated answer cites the retrieved source.
5. Chunk Boundary Issues
Important context could be split between chunks if overlap is insufficient.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
                         THE UNOFFICIAL GUIDE — RAG PIPELINE
                       (Off-campus housing near Nashville unis)

  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 1. DOCUMENT INGESTION                                                      │
  │    Reddit threads ── via .json endpoint (requests)                         │
  │    Web guides/articles/portal ── requests + BeautifulSoup                  │
  │    -> save raw text per source to documents/raw/*.txt  (consistent format) │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                  │  raw .txt files
                                  v
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 2. CLEANING + CHUNKING                                                     │
  │    clean: strip HTML tags, nav/footers/cookie banners, share buttons,      │
  │           "Read more" links, HTML entities (&amp; &nbsp;), boilerplate     │
  │    chunk: 400-600 words, 75-100 word overlap, split on structure first     │
  │           (Reddit -> per comment/group, guides -> per section heading)     │
  │    -> documents/clean/*.txt and documents/chunks/chunks.jsonl              │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                  │  chunks (+ source metadata)
                                  v
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 3. EMBEDDING + VECTOR STORE                                                │
  │    sentence-transformers all-MiniLM-L6-v2  ->  ChromaDB (persistent)       │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  v
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 4. RETRIEVAL          top-k = 5 nearest chunks (cosine) from ChromaDB      │
  └──────────────────────────────┬───────────────────────────────────────────┘
                                  │  query + retrieved chunks + sources
                                  v
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ 5. GENERATION         Groq LLM, grounded on retrieved chunks, cites source │
  │                       Interface: Gradio / Streamlit                        │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will give Claude (in Cursor) my Documents section, my Chunking Strategy section, and the
Architecture diagram above. I'll ask it to implement three scripts: `src/ingest.py` (loads all
10 sources — Reddit via the `.json` endpoint, web pages via `requests` + BeautifulSoup — and
writes raw text to `documents/raw/`), `src/clean.py` (strips HTML, nav, footers, cookie banners,
share/"read more" links, and HTML entities while keeping the substantive review/guide text plus
context like neighborhood and complex names), and `src/chunk.py` (structure-aware chunking at
400–600 words with 75–100 word overlap). I'll verify by inspecting one cleaned document and 5
representative chunks, and by confirming the total chunk count lands between 50 and 2,000.

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
