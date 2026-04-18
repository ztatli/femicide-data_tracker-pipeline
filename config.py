# -*- coding: utf-8 -*-
"""
Femicide Automation Project — Konfigürasyon
Tüm keyword, kategori ve ayarlar burada merkezi olarak tutulur.
"""

# ── Keyword → Kategori Eşleştirmesi ─────────────────────────────────────────

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

# Tüm keyword'ler düz liste (hızlı kontrol için)
ALL_KEYWORDS = [kw for kws in CATEGORY_KEYWORDS.values() for kw in kws]

# Dava/soruşturma kategorisi için zorunlu bağlam kelimeleri.
# Bir haber sadece dava keyword içeriyorsa (topic keyword yok),
# bu listeden en az biri de geçmeli — yoksa haber atılır.
DAVA_CONTEXT_WORDS = [
    "kadın", "kız", "çocuk", "anne", "bebek",
    "karısı", "eşini", "eşi", "kızını", "kızı",
    "sevgilisi", "nişanlısı",
]


# ── Şüpheli Yakınlık Kalıpları ───────────────────────────────────────────────

SUSPECT_PATTERNS = {
    "eş / koca": ["kocası", "eşi", "kocasından", "eşinden", "eski kocası", "eski eşi"],
    "partner": ["sevgilisi", "eski sevgilisi", "nişanlısı", "eski nişanlısı", "partneri"],
    "aile": ["babası", "ağabeyi", "kardeşi", "amcası", "dayısı", "oğlu", "kayınpederi", "erkek kardeşi"],
    "yabancı": ["kimliği belirsiz", "tanımadığı", "komşusu"],
    "belirsiz": [],  # default
}


# ── RSS Deneme URL Şablonları ────────────────────────────────────────────────

RSS_PATHS = [
    "/rss",
    "/rss.xml",
    "/feed",
    "/feed/rss",
    "/feed.rss",
    "/rss/all",
    "/atom.xml",
]


# ── Tarih Filtresi ───────────────────────────────────────────────────────────

def get_target_months():
    """
    Hangi ay(lar)ın taranacağını döndürür.
    Kural:
      - Ayın 1-7. günleri arasındaysa → önceki ay + bu ay
      - Diğer günlerde → sadece bu ay
    Döndürür: list of (yıl, ay) tuple'ları, örn: [(2026, 4)] veya [(2026, 3), (2026, 4)]
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


# ── Bağlam Kelimeleri (Context Words) ───────────────────────────────────────
# Bir haber bu listeden EN AZ BİR kelime içermiyorsa ve keyword sadece özette
# geçiyorsa (başlıkta değil), haber atılır.
# Bu liste çok dar tutulmuştur — gerçek haberi kaçırmamak öncelik.

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


# ── Kaynak Dışlama Listesi ───────────────────────────────────────────────────
# Gazete olmayan ya da istenmeyen domain'ler — 01_build_sources.py bunları atlar.
# Yeni bir sorunlu site çıkarsa buraya ekle.

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


# ── Genel Ayarlar ────────────────────────────────────────────────────────────

IL = "İstanbul"
SOURCES_FILE = "sources/istanbul_sources.csv"
OUTPUT_DIR = "output"
REQUEST_DELAY = 1.5      # saniye — sunucuları yormamak için
REQUEST_TIMEOUT = 10     # saniye
