# -*- coding: utf-8 -*-
"""
01_build_sources.py
-------------------
bilgit.com'daki İstanbul yerel gazete listesini çeker ve
sources/istanbul_sources.csv dosyasına kaydeder.

Bu script sadece bir kez (veya kaynakları güncellemek istediğinde) çalıştırılır.
Çalıştırma: python 01_build_sources.py
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
        print(f"  [HATA] {url} → {e}")
        return None


def normalize_url(href, base):
    """Relative URL'leri absolute'e çevirir, geçersizleri filtreler."""
    if not href or href.startswith(("mailto:", "javascript:", "#")):
        return None
    url = urljoin(base, href.strip())
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    return url


def is_newspaper_url(url):
    """
    bilgit.com içindeki navigasyon linklerini elemeye çalışır.
    Gerçek gazete URL'leri genellikle bilgit.com dışına çıkar.
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
    print(f"bilgit.com → İstanbul gazeteleri çekiliyor...")
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

    print(f"  → {len(results)} gazete bulundu.")
    return results


def save_sources(sources):
    with open(SOURCES_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["gazete_adi", "url", "il"])
        writer.writeheader()
        writer.writerows(sources)
    print(f"\nKaydedildi: {SOURCES_FILE} ({len(sources)} satır)")
    print("İpucu: Bu dosyayı Excel'de açıp yanlış/gereksiz satırları silebilirsin.")


def main():
    sources = scrape_bilgit_istanbul()

    if not sources:
        print("Hiç kaynak bulunamadı. Lütfen site yapısını kontrol et.")
        return

    # İlk 10'u önizle
    print("\n── İlk 10 Sonuç (önizleme) ──")
    for s in sources[:10]:
        print(f"  {s['gazete_adi']:<35} {s['url']}")

    save_sources(sources)


if __name__ == "__main__":
    main()
