# -*- coding: utf-8 -*-
"""
01_build_sources.py
-------------------
Scrapes the local newspaper directory on bilgit.com for Istanbul
and saves the results to sources/istanbul_sources.csv.

Run once per city, or whenever the source list needs updating.
Usage: python 01_build_sources.py
"""

import csv
import time
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from config import IL, SOURCES_FILE, REQUEST_DELAY, REQUEST_TIMEOUT, EXCLUDE_DOMAINS

BILGIT_URL = "https://www.bilgit.com/gazete/34istanbul.html"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(f"  [ERROR] {url} → {e}")
        return None


def normalize_url(href, base):
    """Converts relative URLs to absolute; returns None for invalid ones."""
    if not href or href.startswith(("mailto:", "javascript:", "#")):
        return None
    url = urljoin(base, href.strip())
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    return url


def is_newspaper_url(url):
    """
    Filters out bilgit.com internal navigation links and excluded domains.
    Real newspaper URLs point to external sites.
    """
    if not url:
        return False
    parsed = urlparse(url)
    if "bilgit.com" in parsed.netloc:
        return False
    if any(d in parsed.netloc for d in EXCLUDE_DOMAINS):
        return False
    return True


def scrape_bilgit_istanbul():
    print(f"bilgit.com → Fetching Istanbul newspaper list...")
    html = fetch_page(BILGIT_URL)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen_urls = set()

    for a_tag in soup.find_all("a", href=True):
        url = normalize_url(a_tag["href"], BILGIT_URL)
        if not url or not is_newspaper_url(url):
            continue
        if url in seen_urls:
            continue

        name = a_tag.get_text(strip=True)
        if not name or len(name) < 3:
            continue

        seen_urls.add(url)
        results.append({"gazete_adi": name, "url": url, "il": IL})

    print(f"  → {len(results)} sources found.")
    return results


def save_sources(sources):
    with open(SOURCES_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["gazete_adi", "url", "il"])
        writer.writeheader()
        writer.writerows(sources)
    print(f"\nSaved: {SOURCES_FILE} ({len(sources)} rows)")
    print("Tip: Open in Excel to review and remove any non-news entries.")


def main():
    sources = scrape_bilgit_istanbul()

    if not sources:
        print("No sources found. Check the site structure.")
        return

    print("\n── First 10 results (preview) ──")
    for s in sources[:10]:
        print(f"  {s['gazete_adi']:<35} {s['url']}")

    save_sources(sources)


if __name__ == "__main__":
    main()
