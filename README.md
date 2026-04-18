# Femicide & Violence Against Women — News Scraping Pipeline
### Kadın Cinayetleri & Şiddeti — Haber Toplama Otomasyonu

---

## 🇬🇧 English

### About

This project automates the collection of news about femicide, suspicious deaths, sexual violence, and violence against women and children in Turkey.

It was built as a volunteer contribution to the **[We Will Stop Femicide Platform](https://www.kadincinayetlerinidurduracagiz.net/)** — a civil society organization that tracks and publishes monthly reports on femicide and violence against women in Turkey.

### The Problem

Turkey has 81 provinces, each with dozens of local news outlets. Monitoring all of them for relevant cases — femicide, suspicious deaths, sexual violence, missing persons — requires scanning hundreds of websites manually. This demands a significant volunteer workforce and is prone to coverage gaps and delays.

Previously, volunteers would:
1. Browse local newspaper websites daily or weekly
2. Identify relevant articles by reading headlines
3. Manually submit article URLs via a Google Form
4. Compile data at the end of each month for the platform's report

### The Solution

An automated Python pipeline that:
- Scrapes a directory of local newspaper websites per city
- Detects RSS feeds where available; falls back to HTML scraping
- Filters articles using a curated keyword list across 6 categories
- Classifies each article (femicide, suspicious death, violence, missing person, sexual violence/child abuse, court follow-up)
- Saves structured output to monthly CSV files — ready for reporting or dashboard use

### Impact

| Before | After |
|--------|-------|
| Manual daily/weekly browsing | Automated weekly scan |
| Single volunteer coverage | Scalable to all 81 provinces |
| Google Form submissions (links only) | Structured CSV with category, city, month, suspect relationship |
| Hours of volunteer time per month | Minutes to run the pipeline |

The structured output can feed directly into a reporting dashboard, enabling faster and more consistent monthly reports for the platform.

### Categories Tracked

| Category | Examples |
|----------|---------|
| Femicide | Murder, bodies found, killed by partner |
| Suspicious Death | Suspicious circumstances, suspicious suicide |
| Violence | Domestic abuse, assault, stabbing |
| Missing Person | Missing women, girls, children |
| Sexual Violence / Child Abuse | Rape, child abuse |
| Court / Investigation | Trial updates, arrests, verdicts in related cases |

### Tech Stack

- **Python 3** — scraping, filtering, output
- **feedparser** — RSS feed parsing
- **requests + BeautifulSoup4** — HTML scraping fallback
- **CSV** — structured monthly output

### Project Structure

```
FemicideProject/
│
├── config.py                  # Keywords, categories, settings
├── 01_build_sources.py        # Scrape directory sites → build newspaper source list
├── 02_scrape_news.py          # Weekly scraper → filter → write to CSV
│
├── sources/
│   └── istanbul_sources.csv   # Curated list of Istanbul local newspapers
│
└── output/
    ├── haberler_2026_04.csv   # New incident articles — April 2026
    └── davalar_2026_04.csv    # Court/investigation follow-ups — April 2026
```

### How to Run

**1. Install dependencies**
```bash
pip install requests beautifulsoup4 feedparser
```

**2. Build the source list (run once per city)**
```bash
python 01_build_sources.py
```
Review `sources/istanbul_sources.csv` and remove any non-news entries.

**3. Run the weekly scraper**
```bash
python 02_scrape_news.py
```
Output is saved to `output/haberler_YYYY_MM.csv` and `output/davalar_YYYY_MM.csv`.

### Output CSV Columns

| Column | Description |
|--------|-------------|
| `haber_linki` | Article URL |
| `il` | Province (city) |
| `ay` | Month (YYYY-MM) |
| `kategori` | Incident category |
| `kadin_adi` | Victim name / initials (filled manually) |
| `suphe_yakinlik` | Suspect relationship (auto-detected where possible) |
| `haber_basligi` | Article headline |
| `kaynak_gazete` | Source newspaper |

### Roadmap

- [ ] Extend to all 81 Turkish provinces (per-city output files)
- [ ] Historical data extraction for past months
- [ ] Power BI / Looker Studio dashboard

---

## 🇹🇷 Türkçe

### Hakkında

Bu proje, Türkiye'de kadın cinayetleri, şüpheli ölümler, cinsel şiddet ve kadına/çocuğa yönelik şiddet haberlerini otomatik olarak toplamak için geliştirilmiş bir Python pipeline'ıdır.

**[Kadın Cinayetlerini Durduracağız Platformu](https://www.kadincinayetlerinidurduracagiz.net/)** için gönüllü katkı olarak oluşturulmuştur. Platform, Türkiye'deki kadın cinayetlerini ve şiddet vakalarını takip ederek aylık raporlar yayınlamaktadır.

### Sorun

Türkiye'nin 81 ilinde yüzlerce yerel haber kaynağı bulunmaktadır. Tüm bu kaynakları kadın cinayeti, şüpheli ölüm, cinsel şiddet ve kayıp haberleri açısından takip etmek büyük bir gönüllü iş gücü gerektirmekte ve kapsama boşluklarına yol açmaktadır.

Önceki süreçte gönüllüler:
1. Yerel gazete sitelerini günlük/haftalık olarak manuel tarıyor
2. İlgili haberleri başlık okuyarak tespit ediyor
3. Haber linklerini Google Form aracılığıyla bildiriyor
4. Ay sonunda veriler derlenerek rapor hazırlanıyordu

### Çözüm

Otomatik bir Python pipeline'ı:
- Şehir bazında yerel gazete sitelerini otomatik olarak listeler
- RSS feed bulunursa önce RSS'i okur; bulamazsa HTML scraping yapar
- Haberleri 6 kategori için özenle hazırlanmış keyword listesiyle filtreler
- Her haberi kategorilere ayırır ve aylık CSV dosyalarına kaydeder

### Etki

| Öncesi | Sonrası |
|--------|---------|
| Manuel günlük/haftalık tarama | Otomatik haftalık tarama |
| Tek gönüllü kapsamı | 81 ile ölçeklenebilir |
| Sadece link bildirimi (Google Form) | Kategori, il, ay, şüpheli yakınlığı içeren yapılandırılmış CSV |
| Aylarca gönüllü saati | Dakikalar içinde çalışan pipeline |

Yapılandırılmış çıktı, doğrudan raporlama dashboard'una beslenebilir; aylık raporlar daha hızlı ve tutarlı hale gelir.

### Takip Edilen Kategoriler

| Kategori | Örnekler |
|----------|---------|
| Kadın Cinayeti | Cinayet, ölü bulunan, partner tarafından öldürülen |
| Şüpheli Ölüm | Şüpheli ölüm, şüpheli intihar |
| Şiddet | Aile içi şiddet, darp, bıçaklama |
| Kayıp Haberi | Kayıp kadın, kız, çocuk |
| Cinsel Şiddet / Çocuk İstismarı | Tecavüz, çocuk istismarı |
| Dava / Soruşturma | Yargılama güncellemeleri, tutuklama, beraat kararları |

### Teknik Stack

- **Python 3** — scraping, filtreleme, çıktı
- **feedparser** — RSS feed okuma
- **requests + BeautifulSoup4** — HTML scraping (RSS bulunamazsa)
- **CSV** — aylık yapılandırılmış çıktı

### Nasıl Çalıştırılır

**1. Kütüphaneleri yükle**
```bash
pip install requests beautifulsoup4 feedparser
```

**2. Kaynak listesini oluştur (şehir başına bir kez)**
```bash
python 01_build_sources.py
```
`sources/istanbul_sources.csv` dosyasını kontrol et, gazete olmayan satırları sil.

**3. Haftalık taramayı çalıştır**
```bash
python 02_scrape_news.py
```
Çıktı `output/haberler_YYYY_MM.csv` ve `output/davalar_YYYY_MM.csv` dosyalarına kaydedilir.

---

*Volunteer Data Analyst — Zehra Tatli*
