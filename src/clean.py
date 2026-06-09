"""Milestone 3 — Stage 2a: Cleaning.

Turns each raw file in documents/raw/ into clean, substantive text in
documents/clean/. The goal: keep the actual review/opinion/guide text (plus the
context needed to understand it, like neighborhood or apartment-complex names),
and remove everything that isn't content.

REMOVE: HTML tags, nav menus, cookie/consent banners, ads, footers, repeated
site headers, "Read more"/share/subscribe widgets, comment-count chrome, and
HTML entities (&amp;, &nbsp;).
KEEP:   review text, opinions, ratings, descriptions, and identifying context.

Two paths:
  - web   -> parse HTML, isolate the main content container, drop boilerplate.
  - reddit-> raw is already structured plain text (title + comment bodies);
             just normalize entities/whitespace and drop deleted markers.

Usage:  python -m src.clean
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "documents" / "raw"
CLEAN_DIR = PROJECT_ROOT / "documents" / "clean"

HEADER_SEP = "=" * 70

# Tags that never contain substantive content.
STRIP_TAGS = [
    "script", "style", "noscript", "nav", "header", "footer", "aside",
    "form", "button", "iframe", "svg", "figure", "figcaption", "template",
]

# Always boilerplate on a web page, removed regardless of size. (Reader comment
# sections, cookie/consent bars, share/social widgets, ads, signup forms.) Note:
# Reddit comments are OUR content but arrive via the reddit path, not clean_web,
# so stripping "comment" containers here is safe.
ALWAYS_REMOVE_HINTS = re.compile(
    r"cookie|consent|gdpr|newsletter|subscribe|share|social|promo|advert|"
    r"\bads?\b|sponsor|popup|modal|\bcomment|respond|disqus|leave-a-comment",
    re.I,
)

# Ambiguous tokens that sometimes appear in legitimate content containers
# (e.g. a story wrapper class "...-sidebar-mode-single"). Only removed when the
# element holds little text, so we don't nuke the article body.
AMBIGUOUS_HINTS = re.compile(
    r"related|recommend|sidebar|menu|breadcrumb|site-header|site-footer|"
    r"\bnav\b|banner|skip-link|back-to-top",
    re.I,
)

# Common containers that hold the real article/post body, best-first.
CONTENT_SELECTORS = [
    "article",
    "[class*=story-body]", "[class*=post-content]", "[class*=entry-content]",
    "[class*=article-body]", "[class*=post-body]", "[itemprop=articleBody]",
    "main",
]

# Lines we drop outright after text extraction (leftover UI text).
JUNK_LINE = re.compile(
    r"^(read more|share this|share on|tweet|follow us|sign up|subscribe|"
    r"advertisement|related (stories|posts)|leave a comment|\d+ comments?|"
    r"skip to content|menu|search)\s*$",
    re.I,
)


def parse_header(raw_text: str) -> tuple[dict, str]:
    """Split the metadata header we wrote in ingest.py from the body."""
    head, _, body = raw_text.partition(HEADER_SEP)
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip().lower()] = v.strip()
    return meta, body.lstrip("\n")


def normalize_text(text: str) -> str:
    """Unescape HTML entities, drop zero-width chars, collapse whitespace."""
    text = html.unescape(text)                 # &amp; -> &, &nbsp; -> space
    text = text.replace("\u200b", "").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ newlines to a paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if JUNK_LINE.match(stripped):
            continue
        cleaned_lines.append(stripped)
    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def clean_web(body_html: str) -> str:
    """Isolate the main content of an HTML page and return paragraph text."""
    soup = BeautifulSoup(body_html, "html.parser")

    for tag in soup(STRIP_TAGS):
        tag.decompose()

    # Always-boilerplate elements (comments, cookie bars, share widgets, ads)
    # are removed regardless of size; ambiguous ones only when they're small.
    for attr in ("class", "id"):
        for el in soup.find_all(attrs={attr: ALWAYS_REMOVE_HINTS}):
            el.decompose()
        for el in soup.find_all(attrs={attr: AMBIGUOUS_HINTS}):
            if len(el.get_text(" ", strip=True)) < 400:
                el.decompose()

    # Find the densest known content container; else fall back to the largest div.
    container = None
    for selector in CONTENT_SELECTORS:
        candidates = soup.select(selector)
        if candidates:
            container = max(candidates, key=lambda e: len(e.get_text(" ", strip=True)))
            break
    if container is None:
        divs = soup.find_all("div")
        container = max(divs, key=lambda d: len(d.get_text(" ", strip=True)), default=soup)

    # Pull block-level elements so paragraph structure survives for chunking.
    blocks = container.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"])
    if blocks:
        parts = [b.get_text(" ", strip=True) for b in blocks]
    else:
        parts = [container.get_text("\n", strip=True)]

    text = "\n\n".join(p for p in parts if p)
    return normalize_text(text)


def clean_reddit(body_text: str) -> str:
    """Reddit raw is already plain text; just normalize and drop empties."""
    return normalize_text(body_text)


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("*.txt"))
    if not raw_files:
        print("No raw files found. Run `python -m src.ingest` first.")
        return

    for raw_path in raw_files:
        meta, body = parse_header(raw_path.read_text(encoding="utf-8"))
        kind = meta.get("source_kind", "web")
        cleaned = clean_reddit(body) if kind == "reddit" else clean_web(body)

        out_path = CLEAN_DIR / raw_path.name
        header = [
            f"SOURCE_ID: {meta.get('source_id', '?')}",
            f"SOURCE_NAME: {meta.get('source_name', '?')}",
            f"SOURCE_KIND: {kind}",
            f"SOURCE_URL: {meta.get('source_url', '?')}",
            HEADER_SEP,
            "",
        ]
        out_path.write_text("\n".join(header) + cleaned, encoding="utf-8")
        words = len(cleaned.split())
        flag = "  <-- very little content (JS-rendered? blocked?)" if words < 30 else ""
        print(f"{raw_path.name}: {words:,} words{flag}")


if __name__ == "__main__":
    main()
