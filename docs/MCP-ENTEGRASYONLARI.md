# MCP Entegrasyonları — Mevcut ve Önerilen

Bu doküman, Intyx Dynamic Widget sistemine entegre edilmiş ve edilebilecek tüm MCP (Model Context Protocol) veri kaynaklarını listeler.

---

## Mevcut Entegrasyonlar

Sisteme halihazırda entegre edilmiş 5 veri kaynağı:

| Veri Kaynağı | API / Sağlayıcı | Tool'lar | API Key |
|---|---|---|---|
| **Hava Durumu** | OpenWeatherMap | `get_current_weather`, `get_weather_forecast`, `get_weather_by_coords` | Gerekli |
| **Haberler** | NewsAPI.org | `get_data_sources` (news) | Gerekli |
| **Burç Yorumu** | Gemini AI (üretilen) | `get_data_sources` (horoscope) | Gemini key |
| **Viral Trendler** | Google Trends RSS + Twitter/X | `get_trends`, `suggest_from_trends` | Opsiyonel (Twitter) |
| **Tatil / Özel Günler** | Yerleşik veritabanı (24 gün) | `get_today_holidays`, `get_holidays_by_date`, `get_upcoming_holidays`, `get_holidays_for_month`, `suggest_widget_for_holiday` | Yok (built-in) |

---

## Önerilen Yeni Entegrasyonlar

Aşağıdaki entegrasyonlar projeye eklenebilir. Her biri için:
- **Ne işe yarar** — Hangi widget senaryolarını mümkün kılar
- **API** — Ücretsiz veya düşük maliyetli API kaynağı
- **Öncelik** — Etki ve uygulama kolaylığına göre

---

### Yüksek Öncelik

---

#### 1. Hava Kalitesi (Air Quality)

**Ne işe yarar:**
- "Bugün hava kalitesi kötü, dışarı çıkmayın" uyarı widget'i
- PM2.5 / AQI değerine göre sağlık önerisi widget'i
- Mevcut hava durumu MCP'siyle birleştirildiğinde çok daha zengin bağlam

**Önerilen Tool'lar:**
```
get_air_quality(city)         → AQI, PM2.5, PM10, ozon seviyesi
get_air_quality_by_coords(lat, lon)
suggest_widget_for_air_quality(aqi_value)
```

**Widget Senaryoları:**
- AQI > 150 → "Hava kalitesi kötü, maske takın" banner
- AQI > 200 → "Sağlık uyarısı" alarm widget'i
- Hafta sonu + temiz hava → "Piknik zamanı!" banner

**API Kaynakları:**
- [WAQI (World Air Quality Index)](https://aqicn.org/api/) — Ücretsiz API key, 1000 req/gün
- [OpenAQ](https://openaq.org/) — Tamamen ücretsiz, açık kaynak
- [IQAir](https://www.iqair.com/air-pollution-data-api) — Ücretsiz tier (10.000 req/ay)

**Env Değişkeni:** `WAQI_API_KEY`

---

#### 2. Deprem Verileri

**Ne işe yarar:**
- Deprem sonrası otomatik güvenlik bilgilendirme widget'i
- "Bölgenizde X büyüklüğünde deprem oldu" anlık bildirim widget'i
- Türkiye pazarı için kritik öneme sahip

**Önerilen Tool'lar:**
```
get_recent_earthquakes(min_magnitude, region, hours_back)
get_earthquakes_by_coords(lat, lon, radius_km)
check_earthquake_alert(lat, lon)  → trigger için
```

**Widget Senaryoları:**
- M > 4.0 yakın bölgede → "Deprem güvenlik bilgisi" acil widget
- M > 5.0 → "Acil toplanma noktanızı kontrol edin" banner
- Sismik aktivite yüksekse → "Deprem çantanızı hazırlayın" hatırlatma

**API Kaynakları:**
- [USGS Earthquake API](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) — **Tamamen ücretsiz, API key yok**
- [Kandilli Rasathanesi](http://www.koeri.boun.edu.tr/scripts/lst0.asp) — Türkiye verileri (HTML scraping gerekli)
- [AFAD](https://deprem.afad.gov.tr/) — Resmi Türkiye deprem verileri

**Env Değişkeni:** Yok (USGS tamamen açık)

---

#### 3. Döviz Kurları (Exchange Rates)

**Ne işe yarar:**
- TL/USD, TL/EUR kuru belirli eşiği geçince uyarı widget'i
- Finans uygulamaları için anlık kur gösterge widget'i
- Seyahat uygulamaları için kur karşılaştırma widget'i

**Önerilen Tool'lar:**
```
get_exchange_rates(base_currency, target_currencies)  → {"USD": 32.5, "EUR": 35.2, ...}
get_currency_change(base, target, hours)              → yüzde değişim
suggest_widget_for_rate_change(currency_pair, change_pct)
```

**Widget Senaryoları:**
- TL/USD günlük %2+ değişim → "Döviz dalgalanması" uyarı widget'i
- Her sabah → güncel kur gösterge widget'i
- Kur düşüşü → "Alım fırsatı" banner (finans uygulamaları)

**API Kaynakları:**
- [Open Exchange Rates](https://openexchangerates.org/) — Ücretsiz tier (1000 req/ay)
- [exchangerate-api.com](https://www.exchangerate-api.com/) — Ücretsiz tier (1500 req/ay)
- [Fixer.io](https://fixer.io/) — Ücretsiz tier (100 req/ay)
- [TCMB (Merkez Bankası)](https://www.tcmb.gov.tr/kurlar/today.xml) — **Ücretsiz, Türkiye resmi**

**Env Değişkeni:** `EXCHANGE_RATE_API_KEY`

---

#### 4. Namaz Vakitleri (Prayer Times)

**Ne işe yarar:**
- Türkiye ve Orta Doğu pazarları için son derece değerli
- Namaz vakti yaklaşınca otomatik hatırlatma widget'i
- Ramazan dönemi için özel iftar/sahur widget'leri

**Önerilen Tool'lar:**
```
get_prayer_times(city, country, date)    → {"fajr": "05:32", "dhuhr": "12:45", ...}
get_next_prayer(city, country)           → {"name": "Asr", "time": "15:30", "in_minutes": 45}
get_ramadan_times(city, country, date)   → {"iftar": "19:12", "sahur": "04:58"}
```

**Widget Senaryoları:**
- 15 dk kala → "Öğle namazına 15 dakika kaldı" hatırlatma
- Ramazan'da akşam → "İftar vakti yaklaşıyor" banner
- Yeni ay → "Ramazan başladı" tebrik widget'i

**API Kaynakları:**
- [Aladhan API](https://aladhan.com/prayer-times-api) — **Tamamen ücretsiz, API key yok**
  - Destekler: 10+ hesaplama yöntemi, 200+ şehir
  - Endpoint: `https://api.aladhan.com/v1/timingsByCity`

**Env Değişkeni:** Yok (tamamen ücretsiz)

---

### Orta Öncelik

---

#### 5. Kripto Para Fiyatları (Crypto Prices)

**Ne işe yarar:**
- Bitcoin/Ethereum fiyat değişiminde anlık bildirim widget'i
- Kripto portfolyo izleme uygulamaları için fiyat widget'leri
- "BTC bu hafta %10 düştü" trend bilgisi widget'i

**Önerilen Tool'lar:**
```
get_crypto_price(coin_id, vs_currency)              → {"price": 65000, "change_24h": -2.3}
get_crypto_trending()                               → en çok yükselen/düşen coinler
suggest_widget_for_crypto_change(coin, change_pct)
```

**Widget Senaryoları:**
- BTC günlük ±5% → "Kripto dalgalanması" uyarı widget'i
- Yeni ATH → "Bitcoin rekor kırdı!" kutlama banner'ı
- Finans uygulamaları → portföy özeti widget'i

**API Kaynakları:**
- [CoinGecko API](https://www.coingecko.com/en/api) — Ücretsiz tier (30 req/dk)
- [CoinMarketCap](https://coinmarketcap.com/api/) — Ücretsiz tier (333 req/gün)
- [Binance API](https://binance-docs.github.io/apidocs/) — **API key gerekmez, limitli**

**Env Değişkeni:** `COINGECKO_API_KEY` (opsiyonel, limiti artırır)

---

#### 6. Canlı Spor Skorları (Live Sports)

**Ne işe yarar:**
- Maç sırasında canlı skor widget'i
- Favorit takımın maç sonucu bildirim widget'i
- "Bugün Beşiktaş oynuyor" hatırlatma banner'ı

**Önerilen Tool'lar:**
```
get_live_matches(sport, league)                → canlı maçlar
get_match_result(match_id)                     → maç sonucu
get_upcoming_matches(team_name, days)          → yaklaşan maçlar
suggest_widget_for_match(team, match_status)
```

**Widget Senaryoları:**
- Maç başlangıcı 1 saat öncesi → "Maça az kaldı!" hatırlatma
- Gol atıldığında → "GOL!" anlık banner (WebSocket gerektirir)
- Maç sonu → "Maç bitti X-Y" özet widget'i

**API Kaynakları:**
- [TheSportsDB](https://www.thesportsdb.com/api.php) — Ücretsiz tier (belirli endpoint'ler)
- [API-Football (RapidAPI)](https://rapidapi.com/api-sports/api/api-football/) — Ücretsiz tier (100 req/gün)
- [football-data.org](https://www.football-data.org/) — Ücretsiz tier (10 req/dk, büyük ligler)

**Env Değişkeni:** `SPORTS_API_KEY`

---

#### 7. Film & Dizi Önerileri (Movies & TV)

**Ne işe yarar:**
- "Bu hafta vizyona giren filmler" keşif widget'i
- Favori dizinin yeni sezon çıkışı bildirim widget'i
- Akşam için film önerisi banner'ı

**Önerilen Tool'lar:**
```
get_trending_movies(region, language)          → haftalık trend filmler
get_trending_shows()                           → trend diziler
get_new_releases(type)                         → yeni çıkanlar
suggest_widget_for_entertainment(context)
```

**Widget Senaryoları:**
- Cuma akşamı → "Bu hafta sonu izleyin" film önerisi
- Yeni sezon çıkışı → "Yeni sezon geldi!" haber banner'ı
- Dizi finalı → "Bu akşam final!" hatırlatma

**API Kaynakları:**
- [TMDB (The Movie Database)](https://developer.themoviedb.org/docs) — **Ücretsiz, API key gerekli**
  - Türkçe dil desteği var
  - Kapsamlı film/dizi/oyuncu veritabanı

**Env Değişkeni:** `TMDB_API_KEY`

---

#### 8. UV İndeksi

**Ne işe yarar:**
- "Bugün UV çok yüksek, güneş kremi kullanın" sağlık widget'i
- Hava durumu MCP'siyle entegre, daha zengin bağlam
- Outdoor aktivite öneri widget'leri

**Önerilen Tool'lar:**
```
get_uv_index(lat, lon)                         → {"uv": 8.5, "risk": "very_high"}
get_uv_forecast(lat, lon, days)
suggest_widget_for_uv(uv_index)
```

**Widget Senaryoları:**
- UV > 6 → "Güneş kremi önerilir" hatırlatma
- UV > 8 → "Güneş tehlikeli, gölgede kalın" uyarı banner'ı
- UV düşük + güneşli → "Harika bir yürüyüş günü!"

**API Kaynakları:**
- [OpenUV](https://www.openuv.io/) — Ücretsiz tier (50 req/gün)
- [OpenWeatherMap One Call API](https://openweathermap.org/api/one-call-3) — Mevcut API key ile (One Call)
- [Open-Meteo](https://open-meteo.com/) — **Tamamen ücretsiz, API key yok**, UV dahil

**Env Değişkeni:** `OPENUV_API_KEY` (opsiyonel; Open-Meteo ile key gerekmez)

---

### Düşük Öncelik

---

#### 9. Trafik Durumu (Traffic)

**Ne işe yarar:**
- "Güzergahınızda yoğun trafik var, erken çıkın" uyarı widget'i
- Navigasyon / ulaşım uygulamaları için bağlam

**Önerilen Tool'lar:**
```
get_traffic_status(origin, destination)
get_route_duration(origin, destination)        → tahmini süre vs normal
```

**API Kaynakları:**
- [TomTom Traffic API](https://developer.tomtom.com/traffic-api/documentation) — Ücretsiz tier (2500 req/gün)
- [HERE Traffic API](https://developer.here.com/products/traffic) — Ücretsiz tier (250K işlem/ay)
- [Google Maps Directions API](https://developers.google.com/maps/documentation/directions) — Ücretli (düşük kullanımda ücretsiz kredi)

**Env Değişkeni:** `TOMTOM_API_KEY`

---

#### 10. Reddit Trendleri

**Ne işe yarar:**
- Google Trends + Twitter'a ek olarak Reddit'ten trend konular
- Belirli topluluklara özel (teknoloji, oyun, finans) trend widget'leri

**Önerilen Tool'lar:**
```
get_reddit_trending(subreddit, limit)          → hot posts
get_reddit_hot_topics(category)
```

**API Kaynakları:**
- [Reddit API](https://www.reddit.com/dev/api/) — Ücretsiz, OAuth gerekli
- Reddit JSON endpoint (`reddit.com/r/popular.json`) — **API key gerekmez**

**Env Değişkeni:** `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` (opsiyonel)

---

#### 11. Borsa / Hisse Fiyatları (Stock Market)

**Ne işe yarar:**
- BIST / NYSE hisse fiyat bildirim widget'leri
- "Piyasalar açıldı" / "Piyasalar kapandı" trigger widget'leri

**Önerilen Tool'lar:**
```
get_stock_price(symbol)                        → {"price": 150.25, "change_pct": 1.3}
get_market_status(market)                      → açık/kapalı
get_top_gainers_losers(market)
```

**API Kaynakları:**
- [Alpha Vantage](https://www.alphavantage.co/) — Ücretsiz tier (25 req/gün)
- [Yahoo Finance (yfinance)](https://pypi.org/project/yfinance/) — **Ücretsiz Python kütüphanesi**
- [Polygon.io](https://polygon.io/) — Ücretsiz tier (5 req/dk)

**Env Değişkeni:** `ALPHAVANTAGE_API_KEY`

---

#### 12. Yerel Etkinlikler (Local Events)

**Ne işe yarar:**
- "Bu hafta sonu yakınınızda konser var" keşif widget'i
- Şehir etkinlik takvimi widget'i

**Önerilen Tool'lar:**
```
get_upcoming_events(city, category, days)       → konser, sergi, spor
get_events_by_coords(lat, lon, radius_km)
```

**API Kaynakları:**
- [Eventbrite API](https://www.eventbrite.com/platform/api) — Ücretsiz API key
- [Ticketmaster Discovery API](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/) — Ücretsiz tier (5000 req/gün)
- [Meetup API](https://www.meetup.com/api/guide/) — Sınırlı ücretsiz erişim

**Env Değişkeni:** `EVENTBRITE_API_KEY`

---

#### 13. RSS Feed (Genel)

**Ne işe yarar:**
- Herhangi bir RSS kaynağından özelleştirilebilir haber/içerik widget'i
- Niş topluluklar için (teknoloji blogları, sektör haberleri)

**Önerilen Tool'lar:**
```
get_rss_feed(url, limit)                       → [{title, link, summary, published}]
get_rss_items_by_keyword(url, keyword)
```

**API Kaynakları:**
- Standart RSS/Atom XML — **API key gerekmez**
- Python `feedparser` kütüphanesi ile doğrudan parse

**Env Değişkeni:** Yok

---

## Entegrasyon Öncelik Özeti

| # | Entegrasyon | Öncelik | API Key | Widget Değeri | Uygulama Zorluğu |
|---|---|---|---|---|---|
| 1 | Hava Kalitesi | Yüksek | Evet (ücretsiz) | Çok Yüksek | Düşük |
| 2 | Deprem Verileri | Yüksek | **Yok** | Yüksek | Düşük |
| 3 | Döviz Kurları | Yüksek | Evet (ücretsiz) | Yüksek | Düşük |
| 4 | Namaz Vakitleri | Yüksek | **Yok** | Yüksek (TR/ME) | Düşük |
| 5 | Kripto Para | Orta | Opsiyonel | Orta | Düşük |
| 6 | Canlı Spor | Orta | Evet (ücretsiz) | Yüksek | Orta |
| 7 | Film & Dizi | Orta | Evet (ücretsiz) | Orta | Düşük |
| 8 | UV İndeksi | Orta | **Yok** (Open-Meteo) | Orta | Düşük |
| 9 | Trafik | Düşük | Evet (ücretsiz) | Orta | Yüksek |
| 10 | Reddit Trendleri | Düşük | Opsiyonel | Düşük | Orta |
| 11 | Borsa | Düşük | Evet (ücretsiz) | Düşük | Orta |
| 12 | Yerel Etkinlikler | Düşük | Evet (ücretsiz) | Orta | Orta |
| 13 | RSS Feed | Düşük | **Yok** | Orta | Çok Düşük |

---

## Yeni Entegrasyon Nasıl Eklenir

Yeni bir MCP veri kaynağı eklemek için 4 adım:

### 1. Data Source Oluştur (`server/data_sources/`)

```python
# server/data_sources/air_quality_source.py
import httpx
from server.config import config

class AirQualitySource:
    BASE_URL = "https://api.waqi.info/feed"

    @staticmethod
    def fetch(city: str) -> dict:
        url = f"{AirQualitySource.BASE_URL}/{city}/?token={config.WAQI_API_KEY}"
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()["data"]
        return {
            "aqi": data["aqi"],
            "dominant_pollutant": data.get("dominentpol"),
            "pm25": data["iaqi"].get("pm25", {}).get("v"),
        }
```

### 2. Handler Oluştur (`server/mcp/handlers/`)

```python
# server/mcp/handlers/air_quality_handlers.py
from server.data_sources.air_quality_source import AirQualitySource

async def get_air_quality(args: dict) -> dict:
    city = args["city"]
    data = AirQualitySource.fetch(city)
    return {"status": "ok", "city": city, **data}
```

### 3. Tool Tanımı Ekle (`server/mcp/tool_definitions.py`)

```python
{
    "name": "get_air_quality",
    "description": "Belirtilen şehir için hava kalitesi indeksini (AQI) ve kirleticileri getirir.",
    "schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Şehir adı (örn. Istanbul, Ankara)"
            }
        },
        "required": ["city"]
    },
    "agent_visible": True  # Gemini agent'ın kullanmasını istiyorsak True
}
```

### 4. Handler Registry'e Ekle (`server/mcp/server.py`)

```python
from server.mcp.handlers import air_quality_handlers

TOOL_HANDLERS = {
    # ... mevcut handler'lar ...
    "get_air_quality": air_quality_handlers.get_air_quality,
}
```

Bu 4 adım sonrası yeni tool hem MCP client'larda hem de `ask` Gemini agent'ında otomatik olarak kullanılabilir hale gelir.

---

## Trigger Senaryosu Örnekleri

Yeni entegrasyonlarla mümkün olacak widget tetikleyici kombinasyonları:

```
Hava Kalitesi + Hava Durumu:
  AQI > 150 AND condition == SUNNY → "Güneşli ama hava kirli, dikkatli olun"

Deprem + Konum:
  magnitude > 4.0 AND distance < 100km → "Bölgenizde deprem oldu — güvende misiniz?"

Namaz Vakti + Günün Saati:
  next_prayer == "Akşam" AND time_until < 15min → "İftar vaktine 15 dk kaldı"

Kripto + Trend:
  BTC change > 5% AND trending_topic contains "Bitcoin" → "Bitcoin gündem"

Spor + Gün:
  team match today AND time_until < 2h → "Maça 2 saat kaldı!"

Döviz + Haber:
  USD/TRY change > 2% AND news_category == "economy" → "Döviz dalgalanması haberleri"
```
