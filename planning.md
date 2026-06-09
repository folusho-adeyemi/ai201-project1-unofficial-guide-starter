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
all-MiniLM-L6-v2 

**Top-k:** 5

**Production tradeoff reflection:**

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
