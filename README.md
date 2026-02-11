# Intyx Dynamic Widget System

Mobil uygulamalara entegre edilebilen, bağlama dayali (contextual) dinamik widget sistemi. Widget'lar; hava durumu, haberler, burc yorumlari, takvimsel olaylar, kullanici davranislari ve gelistirici parametreleri gibi tetikleyicilere (trigger) gore otomatik olarak gosterilir.

## Proje Amaci

Uygulama icerisinde kullaniciya dogru zamanda, dogru icerigi gostermek. Ornegin:
- Hava yagmurluysa "semsiye al" widget'i
- Halloween donemi yaklastiginda tematik kampanya widget'i
- Kullanici belirli bir aksiyonu N kez yaptiysa ozel bir oneri widget'i
- Gelistirici tarafindan tanimlanan ozel parametrelere gore widget gosterimi

## Mimari

```
┌──────────────────────────────────────────────────┐
│                  Flutter Client                   │
│  ┌────────────┐ ┌──────────┐ ┌────────────────┐  │
│  │  Widget UI  │ │ Services │ │  Local Models  │  │
│  └─────┬──────┘ └────┬─────┘ └───────┬────────┘  │
│        │             │               │            │
│        └─────────────┼───────────────┘            │
│                      │                            │
└──────────────────────┼────────────────────────────┘
                       │ REST / Firebase
┌──────────────────────┼────────────────────────────┐
│               Python Backend (Flask)              │
│                      │                            │
│  ┌───────────────────┼───────────────────────┐    │
│  │           Trigger Engine                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ │    │
│  │  │ Seasonal │ │ Weather  │ │ UserAction│ │    │
│  │  │Condition │ │ Match    │ │ Condition │ │    │
│  │  └──────────┘ └──────────┘ └───────────┘ │    │
│  └───────────────────────────────────────────┘    │
│                                                   │
│  ┌───────────────────────────────────────────┐    │
│  │           Data Sources (Pub/Sub)          │    │
│  │  ┌─────────┐ ┌──────┐ ┌──────────────┐   │    │
│  │  │ Weather │ │ News │ │  Horoscope   │   │    │
│  │  └─────────┘ └──────┘ └──────────────┘   │    │
│  └───────────────────────────────────────────┘    │
│                                                   │
│  ┌──────────────┐                                 │
│  │   Firebase   │  (Firestore - widget config,    │
│  │  Admin SDK   │   user state, trigger rules)    │
│  └──────────────┘                                 │
└───────────────────────────────────────────────────┘
```

## Mevcut Durum

### Tamamlanan Parcalar
- **Data Modelleri** (`server/models.py`): Weather, News, Horoscope, Widget, Trigger ve UserAction modelleri
- **Data Source'lar** (`server/data_sources/`): Weather, News, Horoscope kaynaklari (Pub/Sub pattern)
- **Trigger Sistemi** (`server/triggers/`): SeasonalCondition, WeatherMatchCondition, UserActionCondition, DeveloperParamCondition + TriggerEngine
- **Konfigürasyon** (`server/config.py`): Environment-based config (Firebase, polling intervals, server)
- **Proje iskeleti**: Flutter client dizin yapisi, .gitignore, requirements.txt

### Yapilmasi Gerekenler

#### Backend (Python)
- [ ] Flask API endpoint'leri (widget listesi, widget detay, trigger evaluation)
- [ ] Firebase Firestore entegrasyonu (widget tanimlari ve trigger kurallari DB'de)
- [ ] MCP (Model Context Protocol) server implementasyonu
- [ ] Data source'larin gercek API'larla entegrasyonu (su an placeholder)
- [ ] Periyodik data polling mekanizmasi (async scheduler)
- [ ] Widget onceliklendirme ve TTL yonetimi
- [ ] Unit testler

#### Frontend (Flutter)
- [ ] Flutter proje kurulumu (pubspec.yaml, ana yapilandirma)
- [ ] Widget modelleri (server modelleriyle eslesecek sekilde)
- [ ] Widget renderer / UI bileşenleri (farkli widget tipleri icin)
- [ ] Backend service katmani (API haberlesme)
- [ ] Firebase entegrasyonu (Firestore listener'lar)
- [ ] Widget dismiss/interaction state yonetimi
- [ ] Ekranlar (widget listesi, detay vs.)
- [ ] Testler

## Teknoloji Yigini

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.10+, Flask, Firebase Admin SDK |
| Veritabani | Firebase Firestore |
| Frontend | Flutter (Dart) |
| Veri Kaynaklari | Weather API, News API, Horoscope API |
| Test | pytest (backend), Flutter test (frontend) |

## Kurulum

### Backend
```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Degiskenleri
```
FIREBASE_PROJECT_ID=intyx-dynamic-widget
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
WEATHER_POLL_INTERVAL=300
NEWS_POLL_INTERVAL=600
HOROSCOPE_POLL_INTERVAL=3600
HOST=0.0.0.0
PORT=8080
```

## Proje Yapisi
```
intyx-dynamic-widget/
├── server/
│   ├── config.py              # Konfigürasyon
│   ├── models.py              # Veri modelleri
│   ├── requirements.txt       # Python bagimliliklari
│   ├── data_sources/          # Veri kaynaklari (pub/sub)
│   │   ├── weather_source.py
│   │   ├── news_source.py
│   │   └── horoscope_source.py
│   ├── mcp/                   # Model Context Protocol (yapilacak)
│   ├── triggers/              # Tetikleme sistemi
│   │   ├── conditions.py      # Kosul implementasyonlari
│   │   └── engine.py          # Degerlendirme motoru
│   └── tests/                 # Testler (yapilacak)
└── flutter_client/
    └── lib/
        ├── models/            # Dart modelleri (yapilacak)
        ├── screens/           # Ekranlar (yapilacak)
        ├── services/          # Servis katmani (yapilacak)
        └── widgets/           # Widget UI bileşenleri (yapilacak)
```
