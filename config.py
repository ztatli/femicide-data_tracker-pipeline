# -*- coding: utf-8 -*-
"""
Femicide Automation Project — Configuration
Central store for all keywords, categories, and settings.
"""

# ── Keyword → Category Mapping ───────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "kadın cinayeti": [
        "kadın cinayeti",
        "kadın öldürüldü",
        "koca kurbanı",
        "ölü bulundu",
        "hayatını kaybetti",
        "öldürülen kadın",
        "katledilen kadın",
    ],
    "şüpheli ölüm": [
        "şüpheli ölüm",
        "şüpheli intihar",
        "intihar",
        "şüpheyle öldü",
    ],
    "şiddet": [
        "kadına şiddet",
        "karısını dövdü",
        "sevgilisini dövdü",
        "bıçaklandı",
        "boğuldu",
        "ailesinden şiddet gören kadın",
        "dövdü",
        "darp etti",
    ],
    "kayıp haberi": [
        "kayıp kadın",
        "kadın kayıp",
        "kız kayıp",
        "çocuk kayıp",
        "kayıp çocuk",
        "kayıp çocuk bulundu",
        "kayıp kız bulundu",
        "kayıp kadın bulundu",
        "günlerdir kayıp",
        "ortadan kaybolan kadın",
        "ortadan kaybolan kız",
        "ortadan kaybolan çocuk",
    ],
    "cinsel şiddet / çocuk istismarı": [
        "tecavüz",
        "çocuk tecavüzü",
        "çocuk istismarı",
        "cinsel saldırı",
        "cinsel istismar",
    ],
    "dava / soruşturma": [
        "dava açıldı",
        "tutuklandı",
        "beraat",
        "mahkeme",
        "cezaevine",
        "yargılama",
        "soruşturma",
    ],
}

# Flat list of all keywords for fast initial matching
ALL_KEYWORDS = [kw for kws in CATEGORY_KEYWORDS.values() for kw in kws]

# Required context words for court/investigation category.
# If an article only matches court keywords (no topic keyword),
# at least one of these must also appear — otherwise the article is discarded.
DAVA_CONTEXT_WORDS = [
    "kadın", "kız", "çocuk", "anne", "bebek",
    "karısı", "eşini", "eşi", "kızını", "kızı",
    "sevgilisi", "nişanlısı",
]


# ── Suspect Relationship Patterns ────────────────────────────────────────────

SUSPECT_PATTERNS = {
    "eş / koca": ["kocası", "eşi", "kocasından", "eşinden", "eski kocası", "eski eşi"],
    "partner": ["sevgilisi", "eski sevgilisi", "nişanlısı", "eski nişanlısı", "partneri"],
    "aile": ["babası", "ağabeyi", "kardeşi", "amcası", "dayısı", "oğlu", "kayınpederi", "erkek kardeşi"],
    "yabancı": ["kimliği belirsiz", "tanımadığı", "komşusu"],
    "belirsiz": [],  # default fallback
}


# ── RSS Feed URL Patterns ─────────────────────────────────────────────────────

RSS_PATHS = [
    "/rss",
    "/rss.xml",
    "/feed",
    "/feed/rss",
    "/feed.rss",
    "/rss/all",
    "/atom.xml",
]


# ── Date Filter ───────────────────────────────────────────────────────────────

def get_target_months():
    """
    Returns the month(s) to scan.
    Rule:
      - Days 1–7 of the month → previous month + current month
      - All other days → current month only
    Returns: list of (year, month) tuples, e.g. [(2026, 4)] or [(2026, 3), (2026, 4)]
    """
    from datetime import date

    today = date.today()
    months = [(today.year, today.month)]

    if today.day <= 7:
        if today.month == 1:
            months.insert(0, (today.year - 1, 12))
        else:
            months.insert(0, (today.year, today.month - 1))

    return months


# ── Female/Child Context Words ────────────────────────────────────────────────
# Used as a secondary filter: if a keyword match occurs only in the summary
# (not the headline), at least one of these must also be present.
# Kept intentionally broad to avoid missing real cases.

FEMALE_CONTEXT_WORDS = [
    "kadın", "kadin",
    "kız", "kiz",
    "anne",
    "eş", "es",
    "koca",
    "sevgili",
    "gelin",
    "nişanlı", "nisanli",
    "çocuk", "cocuk",
    "bebek",
    "genç", "genc",
]


# ── Source Exclusion List ─────────────────────────────────────────────────────
# Non-news domains excluded by 01_build_sources.py.
# Add any problematic domains here to exclude them permanently.

EXCLUDE_DOMAINS = [
    "free-counters.org",
    "statcounter.com",
    "google-analytics.com",
    "addthis.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "whatsapp.com",
]


# ── General Settings ──────────────────────────────────────────────────────────

IL = "İstanbul"
SOURCES_FILE = "sources/istanbul_sources.csv"
OUTPUT_DIR = "output"
REQUEST_DELAY = 1.5      # seconds between requests — avoids overloading servers
REQUEST_TIMEOUT = 10     # seconds
