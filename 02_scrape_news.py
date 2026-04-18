# -*- coding: utf-8 -*-
"""
02_scrape_news.py
-----------------
sources/istanbul_sources.csv'deki her gazete sitesini tarar.
Önce RSS dener, bulamazsa anasayfadan haber linklerini çeker.
Keyword eşleşen haberleri aylık CSV'lere kaydeder.

Çalıştırma: python 02_scrape_news.py
"""

import csv
import os
import re
import time
from datetime import date, datetime
from urllib.parse import urlparse, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from config import (
    ALL_KEYWORDS,
    CATEGORY_KEYWORDS,
    DAVA_CONTEXT_WORDS,
    IL,
    OUTPUT_DIR,
    REQUEST_DELAY,
    REQUEST_TIMEOUT,
    RSS_PATHS,
    SOURCES_FILE,
    SUSPECT_PATTERNS,
    get_target_months,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

OUTPUT_COLUMNS = [
    "haber_linki",
    "il",
    "ay",
    "kategori",
    "kadin_adi",
    "suphe_yakinlik",
    "haber_basligi",
    "kaynak_gazete",
]


# ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def fetch_html(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception:
        return None


def base_url(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def normalize_text(text):
    """Küçük harfe çevirir, Türkçe karakterleri korur."""
    return text.lower().strip() if text else ""


# ── Keyword & Kategori ───────────────────────────────────────────────────────

DAVA_KATEGORI = "dava / soruşturma"
DAVA_KEYWORDS = CATEGORY_KEYWORDS[DAVA_KATEGORI]
TOPIC_KEYWORDS = [
    kw for cat, kws in CATEGORY_KEYWORDS.items()
    if cat != DAVA_KATEGORI
    for kw in kws
]


def _has_dava_context(text_lower):
    """Dava context kontrolü: kadın/kız/çocuk gibi bağlam kelimesi var mı?"""
    return any(cw in text_lower for cw in DAVA_CONTEXT_WORDS)


def find_category(text):
    """
    Kategori belirleme mantığı:
    - Önce topic keyword (cinayet, şiddet, tecavüz...) aranır.
    - Topic keyword varsa + dava keyword de varsa → dava/soruşturma
    - Topic keyword varsa, dava yoksa → o topic kategorisi
    - Sadece dava keyword varsa → kadın/çocuk bağlamı zorunlu; yoksa atılır
    - Hiç eşleşme yoksa → None (kaydetme)
    """
    text_lower = normalize_text(text)

    topic_cat = None
    for kategori, keywords in CATEGORY_KEYWORDS.items():
        if kategori == DAVA_KATEGORI:
            continue
        if any(kw in text_lower for kw in keywords):
            topic_cat = kategori
            break

    has_dava = any(dk in text_lower for dk in DAVA_KEYWORDS)

    if topic_cat and has_dava:
        return DAVA_KATEGORI
    if topic_cat:
        return topic_cat
    if has_dava and _has_dava_context(text_lower):
        return DAVA_KATEGORI
    return None  # "mahkeme kararı" gibi alakasız davalar buraya düşer → atılır


def has_keyword(title, summary=""):
    """Başlık veya özette herhangi bir keyword var mı? (Geniş ilk filtre)"""
    combined = normalize_text(f"{title} {summary}")
    return any(kw in combined for kw in ALL_KEYWORDS)


# ── Şüpheli Yakınlık ─────────────────────────────────────────────────────────

def find_suspect_relation(text):
    text_lower = normalize_text(text)
    for yakinlik, patterns in SUSPECT_PATTERNS.items():
        if patterns and any(p in text_lower for p in patterns):
            return yakinlik
    return "belirsiz"


# ── Tarih ────────────────────────────────────────────────────────────────────

def parse_date(date_input):
    """
    feedparser'dan gelen time.struct_time veya string'i date'e çevirir.
    Başarısız olursa None döner.
    """
    if date_input is None:
        return None
    try:
        if hasattr(date_input, "tm_year"):
            return date(date_input.tm_year, date_input.tm_mon, date_input.tm_mday)
        formats = ["%a, %d %b %Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(str(date_input)[:16], fmt).date()
            except ValueError:
                continue
    except Exception:
        pass
    return None


def is_in_target_months(article_date, target_months):
    if article_date is None:
        return True  # tarihi bilinmiyorsa dahil et, kullanıcı kontrol eder
    return (article_date.year, article_date.month) in target_months


# ── RSS Scraping ─────────────────────────────────────────────────────────────

def try_rss(site_url):
    """
    Yaygın RSS path'lerini dener, çalışanı döndürür.
    Başarısız olursa None döner.
    """
    base = base_url(site_url)
    for path in RSS_PATHS:
        rss_url = base + path
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                return feed
        except Exception:
            continue
        time.sleep(0.3)
    return None


def articles_from_rss(feed, target_months):
    articles = []
    for entry in feed.entries:
        title = getattr(entry, "title", "") or ""
        link = getattr(entry, "link", "") or ""
        summary = getattr(entry, "summary", "") or ""
        combined_text = f"{title} {summary}"

        if not has_keyword(title, summary):
            continue

        pub_date = parse_date(getattr(entry, "published_parsed", None))
        if not is_in_target_months(pub_date, target_months):
            continue

        articles.append({
            "baslik": title,
            "link": link,
            "tarih": pub_date,
            "metin": combined_text,
        })
    return articles


# ── HTML Scraping (RSS yoksa) ─────────────────────────────────────────────────

def articles_from_html(site_url, target_months):
    """
    Anasayfadan tüm internal linkleri çeker, başlık keyword kontrolü yapar.
    RSS bulunamayan siteler için fallback.
    """
    html = fetch_html(site_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    base = base_url(site_url)
    articles = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue

        link = urljoin(base, href)
        if urlparse(link).netloc != urlparse(base).netloc:
            continue
        if link in seen:
            continue
        seen.add(link)

        title = a.get_text(strip=True)
        if not title or len(title) < 15:
            continue
        if not has_keyword(title):
            continue  # HTML'de sadece başlık var, summary yok

        articles.append({
            "baslik": title,
            "link": link,
            "tarih": None,
            "metin": title,
        })

    return articles


# ── Output CSV ───────────────────────────────────────────────────────────────

def output_path(year, month):
    filename = f"haberler_{year}_{month:02d}.csv"
    return os.path.join(OUTPUT_DIR, filename)


def dava_output_path(year, month):
    filename = f"davalar_{year}_{month:02d}.csv"
    return os.path.join(OUTPUT_DIR, filename)


def load_existing_links(filepath):
    """Tekrar yazımı önlemek için mevcut CSV'deki linkleri yükler."""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {row["haber_linki"] for row in reader}


def append_rows(filepath, rows):
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ── Ana Akış ─────────────────────────────────────────────────────────────────

def process_article(article, gazete_adi):
    """None döndürürse haber atılır (ana döngü kontrol eder)."""
    tarih = article["tarih"]
    ay_str = f"{tarih.year}-{tarih.month:02d}" if tarih else "bilinmiyor"

    kategori = find_category(article["metin"])
    if not kategori:
        return None

    return {
        "haber_linki": article["link"],
        "il": IL,
        "ay": ay_str,
        "kategori": kategori,
        "kadin_adi": "",
        "suphe_yakinlik": find_suspect_relation(article["metin"]),
        "haber_basligi": article["baslik"],
        "kaynak_gazete": gazete_adi,
    }


def main():
    target_months = get_target_months()
    print(f"Hedef ay(lar): {target_months}")

    # pending_haberler → yeni olaylar, pending_davalar → dava/soruşturma takibi
    pending_haberler = {ym: [] for ym in target_months}
    pending_davalar  = {ym: [] for ym in target_months}

    # Mevcut CSV'lerdeki linkleri yükle (tekrar yazımı önle)
    existing_links = {}
    for ym in target_months:
        links = load_existing_links(output_path(*ym))
        links |= load_existing_links(dava_output_path(*ym))
        existing_links[ym] = links

    # Kaynak listesini oku
    if not os.path.exists(SOURCES_FILE):
        print(f"HATA: {SOURCES_FILE} bulunamadı. Önce 01_build_sources.py çalıştır.")
        return

    with open(SOURCES_FILE, encoding="utf-8-sig") as f:
        sources = list(csv.DictReader(f))

    print(f"{len(sources)} gazete kaynağı bulundu.\n")

    total_found = 0

    for i, source in enumerate(sources, 1):
        gazete_adi = source["gazete_adi"]
        site_url = source["url"].strip()
        print(f"[{i}/{len(sources)}] {gazete_adi} → {site_url}")

        # RSS dene
        feed = try_rss(site_url)
        if feed:
            articles = articles_from_rss(feed, target_months)
            method = "RSS"
        else:
            articles = articles_from_html(site_url, target_months)
            method = "HTML"

        new_count = 0
        for art in articles:
            row = process_article(art, gazete_adi)
            if row is None:
                continue

            # Hangi ay dosyasına gidecek?
            if art["tarih"]:
                ym = (art["tarih"].year, art["tarih"].month)
            else:
                today = date.today()
                ym = (today.year, today.month)

            if ym not in pending_haberler:
                continue  # hedef ay dışında
            if row["haber_linki"] in existing_links.get(ym, set()):
                continue  # zaten var

            # Dava/soruşturma ayrımı
            if row["kategori"] == DAVA_KATEGORI:
                pending_davalar[ym].append(row)
            else:
                pending_haberler[ym].append(row)

            existing_links.setdefault(ym, set()).add(row["haber_linki"])
            new_count += 1

        print(f"   [{method}] {new_count} yeni haber bulundu.")
        total_found += new_count
        time.sleep(REQUEST_DELAY)

    # Dosyalara yaz
    print("\n── Dosyalara yazılıyor... ──")
    for ym in target_months:
        haberler = pending_haberler[ym]
        davalar  = pending_davalar[ym]

        if haberler:
            fp = output_path(*ym)
            append_rows(fp, haberler)
            print(f"  {fp} → {len(haberler)} satır eklendi.")

        if davalar:
            fp = dava_output_path(*ym)
            append_rows(fp, davalar)
            print(f"  {fp} → {len(davalar)} dava/soruşturma satırı eklendi.")

    print(f"\nTamamlandı. Toplam {total_found} yeni haber kaydedildi.")


if __name__ == "__main__":
    main()
