# Manual fallback documents

Drop saved copies of blocked/JS-rendered sources here. `src/ingest.py` checks
this folder FIRST and uses your saved file instead of fetching over the network.
Use the EXACT filename in the table below so the ingester matches it to the source.

| # | Source | Save this file here |
|---|--------|---------------------|
| 1 | Vanderbilt Housing Discussion (Reddit)            | `01_vanderbilt_housing_discussion.json` |
| 2 | Off-Campus Housing Culture Question (Reddit)      | `02_offcampus_housing_culture.json` |
| 3 | Transfer Student Housing Thread (Reddit)          | `03_transfer_student_housing.json` |
| 4 | Off-Campus Housing and Roommates (Reddit)         | `04_offcampus_housing_roommates.json` |
| 5 | Housing Recommendations (Reddit)                  | `05_housing_recommendations.json` |
| 6 | Graduate Student Housing Recommendations (Reddit) | `06_grad_student_housing.json` |
| 7 | Broadview vs On-Campus Housing (Reddit)           | `07_broadview_vs_oncampus.json` |
| 8 | Student Housing in Nashville Guide (SPA)          | `08_student_housing_nashville_guide.txt` |
| 10| Vanderbilt Off-Campus Housing Portal              | `10_vanderbilt_offcampus_portal.txt` |

(Source 9 fetches fine automatically, so it doesn't need a manual file.)

## Reddit (.json) — sources 1–7
1. In your normal logged-in browser, open the thread URL with `.json` added, e.g.
   `https://www.reddit.com/r/Vanderbilt/comments/1r39b3j/housing.json`
2. You'll see raw JSON. Save the page (Cmd+S) as the matching `NN_slug.json` above.
3. Repeat for all 7 threads. The ingester parses the post + every comment.

## SPA guide / portal — sources 8 and 10
These render with JavaScript, so saved HTML has no article text. Instead:
1. Open the page in your browser and let it fully load.
2. Select the real content (the guide article / the listings), copy it.
3. Paste into the matching `NN_slug.txt` file above.
(You can also save full-page HTML as `NN_slug.html` if your browser captures the
rendered DOM, but pasted `.txt` is the reliable option.)

## Then re-run the pipeline
```
python -m src.ingest      # picks up manual files automatically
python -m src.clean
python -m src.chunk
python -m src.inspect_chunks 5
```
