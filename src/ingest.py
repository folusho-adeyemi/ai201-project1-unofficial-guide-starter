"""Milestone 3 — Stage 1: Document ingestion.

Loads every source listed in sources.py and writes the RAW extracted text to
documents/raw/NN_slug.txt in a consistent format (a small metadata header
followed by the body). No cleaning happens here on purpose — we save raw first
so cleaning is a separate, inspectable step.

- Reddit threads are fetched via the public `.json` endpoint, which returns the
  post + nested comments as structured JSON (more reliable than scraping HTML).
- Web pages are fetched as HTML; we keep the full HTML body here and defer
  boilerplate removal to clean.py.

Usage:  python -m src.ingest      (run from the project root)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from .sources import SOURCES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "documents" / "raw"
# Drop saved pages here to bypass anti-bot blocks (Reddit/SPA/portal):
#   documents/manual/NN_slug.json  -> a saved Reddit `<url>.json` response
#   documents/manual/NN_slug.html  -> a saved/"View Source" HTML page
#   documents/manual/NN_slug.txt   -> readable text pasted from the page
# If a matching file exists, the ingester uses it instead of the network.
MANUAL_DIR = PROJECT_ROOT / "documents" / "manual"

# A descriptive User-Agent is required by Reddit and is polite for any site.
HEADERS = {
    "User-Agent": "UnofficialGuideBot/1.0 (CodePath AI201 Project 1; educational use)"
}
REQUEST_TIMEOUT = 30


def parse_reddit_json(data) -> str:
    """Render a Reddit thread JSON payload (post + comment forest) as plain text.

    The payload is a 2-item list: [post listing, comments listing]. We walk the
    comment tree recursively so reply chains stay in reading order.
    """
    lines: list[str] = []

    # First listing: the original post.
    post = data[0]["data"]["children"][0]["data"]
    title = post.get("title", "").strip()
    selftext = post.get("selftext", "").strip()
    author = post.get("author", "unknown")
    if title:
        lines.append(f"POST TITLE: {title}")
    lines.append(f"POSTED BY u/{author}")
    if selftext:
        lines.append("")
        lines.append(selftext)

    # Second listing: the comment forest.
    def walk_comments(children, depth=0):
        for child in children:
            if child.get("kind") != "t1":
                continue  # skip "more" stubs and non-comments
            cdata = child["data"]
            body = (cdata.get("body") or "").strip()
            cauthor = cdata.get("author", "unknown")
            if body and body not in ("[deleted]", "[removed]"):
                indent = "  " * depth
                lines.append("")
                lines.append(f"{indent}COMMENT by u/{cauthor}:")
                lines.append(f"{indent}{body}")
            replies = cdata.get("replies")
            if isinstance(replies, dict):
                walk_comments(replies["data"]["children"], depth + 1)

    if len(data) > 1:
        lines.append("")
        lines.append("--- COMMENTS ---")
        walk_comments(data[1]["data"]["children"])

    return "\n".join(lines)


def fetch_reddit(url: str) -> str:
    """Fetch a Reddit thread via its public `.json` endpoint and render to text."""
    json_url = url.rstrip("/") + ".json"
    resp = requests.get(
        json_url, headers=HEADERS, params={"raw_json": 1}, timeout=REQUEST_TIMEOUT
    )
    resp.raise_for_status()
    return parse_reddit_json(resp.json())


def fetch_web(url: str) -> str:
    """Return the raw HTML of a web page. Boilerplate removal happens in clean.py."""
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def load_manual(source: dict) -> str | None:
    """Use a locally saved copy if present, bypassing anti-bot blocks.

    Returns the extracted body, or None if no manual file exists for this source.
    """
    stem = f"{source['id']:02d}_{source['slug']}"
    json_path = MANUAL_DIR / f"{stem}.json"
    html_path = MANUAL_DIR / f"{stem}.html"
    txt_path = MANUAL_DIR / f"{stem}.txt"

    if source["kind"] == "reddit" and json_path.exists():
        return parse_reddit_json(json.loads(json_path.read_text(encoding="utf-8")))
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8")
    return None


def write_raw(source: dict, body: str) -> Path:
    """Write the raw body with a consistent metadata header."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RAW_DIR / f"{source['id']:02d}_{source['slug']}.txt"
    header = [
        f"SOURCE_ID: {source['id']}",
        f"SOURCE_NAME: {source['name']}",
        f"SOURCE_KIND: {source['kind']}",
        f"SOURCE_URL: {source['url']}",
        "=" * 70,
        "",
    ]
    out_path.write_text("\n".join(header) + body, encoding="utf-8")
    return out_path


def main() -> None:
    manifest = []
    for source in SOURCES:
        print(f"[{source['id']:02d}] {source['name']} ... ", end="", flush=True)
        try:
            manual = load_manual(source)
            if manual is not None:
                body, origin = manual, "manual"
            elif source["kind"] == "reddit":
                body, origin = fetch_reddit(source["url"]), "fetched"
            else:
                body, origin = fetch_web(source["url"]), "fetched"
            out_path = write_raw(source, body)
            print(f"ok [{origin}] ({len(body):,} chars) -> {out_path.relative_to(PROJECT_ROOT)}")
            manifest.append(
                {**source, "origin": origin, "raw_file": str(out_path.relative_to(PROJECT_ROOT)), "chars": len(body)}
            )
        except Exception as exc:  # noqa: BLE001 - report and continue with other sources
            print(f"FAILED: {exc}")
            manifest.append({**source, "error": str(exc)})
        time.sleep(1.0)  # be polite; avoid hammering remote hosts

    manifest_path = RAW_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    ok = sum(1 for m in manifest if "raw_file" in m)
    print(f"\nIngested {ok}/{len(SOURCES)} sources. Manifest: {manifest_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
