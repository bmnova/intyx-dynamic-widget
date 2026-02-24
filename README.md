# Intyx Dynamic Widget System

Mobil uygulamalara entegre edilebilen, AI destekli, baglamsal (contextual) dinamik widget sistemi.

Widget'lar; hava durumu, haberler, burc yorumlari, takvimsel olaylar, viral trendler, kullanici davranislari ve gelistirici parametreleri gibi tetikleyicilere (trigger) gore otomatik olarak gosterilir. Gemini AI agent widget icerigi oner ve uretir.

## Proje Amaci

Uygulama icerisinde kullaniciya dogru zamanda, dogru icerigi gostermek. Ornegin:
- Hava yagmurluysa "semsiye al" widget'i
- Halloween donemi yaklastiginda tematik kampanya widget'i
- Kullanici belirli bir aksiyonu N kez yaptiysa ozel bir oneri widget'i
- Twitter/X'te bir konu trend olmusken buna uygun widget
- Gelistirici tarafindan tanimlanan ozel parametrelere gore widget gosterimi

## Bilesenler

| Bilesen | Teknoloji | Aciklama |
|---------|-----------|----------|
| **Backend (server/)** | Python 3.12, Flask, Gunicorn | REST API, trigger engine, data source polling, Gemini AI entegrasyonu |
| **Flutter SDK (flutter_client/)** | Dart, Flutter | pub.dev paketi — 15+ hazir widget tipi, JSON-driven rendering |
| **Web Dashboard (web/)** | React 18, Vite | Widget Studio, Agent Tasks, Pricing, lisans yonetimi |
| **MCP Server (server/mcp/)** | Python, MCP SDK | Cursor/Claude Desktop icin Model Context Protocol sunucusu |
| **Firebase** | Firestore | Widget, trigger, lisans, agent task, data cache depolama |
| **Gemini AI** | Google Generative AI | Widget onerisi, icerik uretimi, agentic tool orchestration |

## Mimari

```
                       Flutter / Web Client
                              |
                         REST API (Flask)
                              |
          +-------------------+-------------------+
          |                   |                   |
    Trigger Engine      Data Sources        Gemini AI Agent
    (conditions.py)     (weather, news,     (suggest, generate,
     (engine.py)         horoscope, trend)   ask — tool orchestration)
          |                   |                   |
          +-------------------+-------------------+
                              |
                    Firebase Firestore
                    (widgets, triggers,
                     licenses, agent_tasks,
                     user_states, data_cache)

    MCP Server (ayri process — Cursor/IDE icin)
       |
       +-- Ayni tool definitions + Gemini agent
```

## Hizli Baslangic

### 1. Backend

```bash
cd server
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env olustur (zorunlu key'ler)
cp .env.example .env
# .env icine GEMINI_API_KEY degerini yaz

# Calistir
python -m server.app
# → http://localhost:8080/api/health
```

### 2. Web Dashboard

```bash
cd web
npm install
npm run dev
# → http://localhost:3000
```

### 3. Flutter SDK

```yaml
# pubspec.yaml
dependencies:
  intyx_dynamic_widget:
    path: ../flutter_client   # veya pub.dev'den
```

```dart
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();
  runApp(MyApp());
}
```

### 4. MCP Server (Cursor/Claude Desktop)

```bash
# mcp_config.example.json icindeki ayarlari IDE'nize kopyalayin
python -m server.mcp
```

## Deployment & Environment Variables

### Lokal Gelistirme (Dev Mode)

Her iki servisi ayri terminallerde calistir:

```bash
# Terminal 1 — Backend
cd server
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .env icine en azindan su iki satiri yaz:
#   GEMINI_API_KEY=<google ai studio'dan alinir>
#   INTYX_DEV_MODE=true     # lisans dogrulamasi bypass edilir
python -m server.app
# → http://localhost:8080/api/health

# Terminal 2 — Frontend
cd web
cp .env.example .env
# .env zaten VITE_API_URL=http://localhost:8080 iceriyor, degistirme
npm install && npm run dev
# → http://localhost:3000
```

`INTYX_DEV_MODE=true` ile backend lisans kontrolu devredisi kalir; gelistirirken her seyi test edebilirsin.
**Bunu asla production ortamina tasima.**

---

### Production Deployment

#### 1. Backend'i deploy et (Railway / Render / Cloud Run / Docker)

Backend, Vercel'e deploy edilemez — Node deil, Python/Flask. Asagidaki platformlardan birini kullan:

| Platform | Ucretsiz tier | Not |
|----------|--------------|-----|
| [Railway](https://railway.app) | Var | En kolay — repo'yu direkt baglayabilirsin |
| [Render](https://render.com) | Var | `server/` klasorunu root olarak sec |
| [Google Cloud Run](https://cloud.run) | Var | Dockerfile hazir, `gcloud run deploy` |

**Zorunlu environment variables (backend):**

```env
FIREBASE_PROJECT_ID=<firebase-proje-adi>
GEMINI_API_KEY=<google-ai-studio-api-key>

# Firebase credentials: Cloud ortamlarda Application Default Credentials kullanilir.
# Lokal veya baska platformlarda service account JSON yolunu goster:
# FIREBASE_CREDENTIALS_PATH=/app/serviceAccountKey.json

# Production'da dev mode'u KAPALI birak (varsayilan zaten kapali):
# INTYX_DEV_MODE=false

# Opsiyonel ama onerilen — admin ve server erisimini korur:
# INTYX_SERVER_API_KEY=<openssl rand -hex 32 ile uret>
```

Deploy ettikten sonra backend URL'ini not et (ornek: `https://intyx-api.railway.app`).

#### 2. Frontend'i Vercel'e deploy et

`web/` klasoru zaten Vercel'e deploy edilmis durumda. Tek eksik: `VITE_API_URL`.

Vercel Dashboard → Project → Settings → Environment Variables:

```
VITE_API_URL = https://intyx-api.railway.app   ← backend URL'ini buraya yaz
```

Bu degiskeni ekleyip **Redeploy** yapinca Widget Studio "Generate Widgets", Agent Tasks ve diger API cagrisi yapan her sey calismaya baslayacak.

**Opsiyonel frontend env variables:**

```env
# Paddle odeme entegrasyonu icin:
VITE_PADDLE_ENV=production
VITE_PADDLE_PUBLISHABLE_TOKEN=live_xxx
VITE_PADDLE_PRICE_IDS={"pro":"pri_xxx","enterprise":"pri_yyy"}

# /admin sayfasini korumak icin (backend INTYX_SERVER_API_KEY ile ayni olmali):
VITE_ADMIN_SECRET=<gizli-anahtar>

# Dashboard/Studio/AgentTasks icin API key zorunlu kilmak istersen:
VITE_REQUIRE_AUTH=true
```

#### Kontrol listesi

- [ ] Firebase projesi olusturuldu ve Firestore aktif
- [ ] Gemini API key alindi (aistudio.google.com)
- [ ] Backend platforma deploy edildi ve `/api/health` 200 doniyor
- [ ] Vercel'de `VITE_API_URL` set edildi ve Redeploy yapildi
- [ ] (Opsiyonel) Paddle entegrasyonu yapildi

---

## Proje Yapisi

```
intyx-dynamic-widget/
├── server/                         # Python Backend
│   ├── app.py                      # Flask app, auth middleware, blueprint registration
│   ├── config.py                   # Tum environment degiskenleri
│   ├── models.py                   # Weather, News, Horoscope, Widget, Trigger, UserAction
│   ├── firebase_client.py          # Firestore CRUD (widget, license, agent_task, cache)
│   ├── scheduler.py                # Periyodik data source polling (async)
│   ├── requirements.txt            # Python bagimliliklari
│   ├── .env.example                # Ornek environment dosyasi
│   ├── ai/
│   │   └── gemini_client.py        # Gemini SDK wrapper + singleton
│   ├── routes/
│   │   ├── widgets.py              # Widget CRUD + evaluate + dismiss + interact
│   │   ├── ai.py                   # /api/ai/suggest-widget, /api/ai/generate-content
│   │   ├── licenses.py             # Lisans olusturma ve dogrulama
│   │   ├── agent_tasks.py          # Agent task/persona CRUD
│   │   ├── trends.py               # Viral trend API
│   │   └── paddle_webhook.py       # Paddle odeme webhook (HMAC-SHA256)
│   ├── data_sources/
│   │   ├── weather_source.py       # OpenWeatherMap entegrasyonu
│   │   ├── news_source.py          # NewsAPI.org entegrasyonu
│   │   ├── horoscope_source.py     # Gemini AI ile burc yorumu
│   │   └── trend_source.py         # Twitter/X trend verisi
│   ├── triggers/
│   │   ├── conditions.py           # Seasonal, Weather, UserAction, DeveloperParam
│   │   └── engine.py               # Trigger degerlendirme motoru
│   ├── mcp/
│   │   ├── server.py               # MCP server — handler registry pattern
│   │   ├── agent.py                # Gemini agent — auto-generated tool declarations
│   │   ├── tool_definitions.py     # 20 tool tanimi (single source of truth)
│   │   └── handlers/
│   │       ├── widget_handlers.py  # Widget CRUD + trigger handlers
│   │       ├── weather_handlers.py # Hava durumu handlers
│   │       ├── holiday_handlers.py # Tatil/ozel gun handlers
│   │       ├── trend_handlers.py   # Trend handlers
│   │       └── ai_handlers.py      # Data source + AI suggest handlers
│   └── tests/
│       ├── test_models.py          # Model testleri
│       ├── test_triggers.py        # Trigger engine testleri
│       ├── test_api.py             # 28 API endpoint testi
│       └── test_data_sources.py    # Data source testleri
│
├── flutter_client/                 # Flutter SDK Paketi
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── intyx_dynamic_widget.dart   # Library export
│   │   ├── catalog/
│   │   │   └── widget_catalog.json     # Widget tipi katalogu (16 tip)
│   │   ├── core/
│   │   │   ├── widget_registry.dart    # type -> Widget eslestirme
│   │   │   ├── widget_resolver.dart    # JSON -> Widget listesi
│   │   │   ├── catalog_provider.dart   # Catalog JSON okuma/sunma
│   │   │   ├── intyx_init.dart         # SDK baslatma
│   │   │   └── responsive_widget_wrapper.dart  # Layout/boyut wrapper
│   │   ├── models/
│   │   │   ├── widget_definition.dart  # WidgetDefinition, WidgetContent
│   │   │   ├── widget_response.dart    # Agent JSON response modeli
│   │   │   └── trigger_context.dart    # TriggerContext (client-side)
│   │   ├── services/
│   │   │   ├── widget_service.dart     # Backend API haberlesme
│   │   │   └── firebase_service.dart   # Firestore realtime listener
│   │   └── widgets/
│   │       ├── dynamic_widget_container.dart  # Ana wrapper
│   │       ├── promotional_widget.dart
│   │       ├── contextual_widget.dart
│   │       ├── informational_widget.dart
│   │       ├── functional_widget.dart
│   │       └── ui/                     # 12 hazir UI widget
│   │           ├── banner_card.dart
│   │           ├── carousel_card.dart
│   │           ├── clickable_image_link_card.dart
│   │           ├── countdown_banner_card.dart
│   │           ├── hero_image_card.dart
│   │           ├── icon_text_action_card.dart
│   │           ├── poll_card.dart
│   │           ├── profile_card.dart
│   │           ├── progress_card.dart
│   │           ├── rating_card.dart
│   │           ├── social_proof_card.dart
│   │           └── title_subtitle_image_card.dart
│   └── test/
│
├── web/                            # React Web Dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── App.jsx                 # React Router setup
│       ├── main.jsx                # Entry point
│       ├── config.js               # API URL config
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ProtectedRoute.jsx  # API key / dev mode guard
│       │   ├── Toast.jsx
│       │   └── WidgetCard.jsx
│       ├── pages/
│       │   ├── Landing.jsx         # Ana sayfa
│       │   ├── Dashboard.jsx       # Kontrol paneli
│       │   ├── WidgetStudio.jsx    # 3-adimli widget olusturma
│       │   ├── AgentTasks.jsx      # Agent task yonetimi
│       │   ├── Pricing.jsx         # Plan/fiyat sayfasi (Paddle)
│       │   └── NotFound.jsx        # 404 sayfasi
│       └── lib/
│           └── paddle.js           # Paddle SDK entegrasyonu
│
├── example/                        # Flutter ornek uygulama
├── functions/                      # Firebase Cloud Functions (opsiyonel Gemini)
├── docs/                           # Dokumantasyon
│   ├── API-KEYS.md                 # Tum API key'ler ve env degiskenleri
│   ├── ARCHITECTURE.md             # Mimari detay dokumani
│   ├── DEPLOY-SERVER.md            # Backend deploy rehberi
│   ├── DEPLOY-WEB.md               # Web deploy rehberi
│   ├── FIREBASE-SETUP.md           # Firebase kurulum rehberi
│   ├── FIREBASE-FUNCTIONS-GEMINI.md # Cloud Functions ile Gemini
│   └── MCP-SERVER.md               # MCP server kullanim rehberi
├── Dockerfile                      # Backend container
├── firebase.json                   # Firebase config
├── firestore.rules                 # Firestore guvenlik kurallari
├── firestore.indexes.json          # Firestore index'leri
├── mcp_config.example.json         # MCP config ornegi (Cursor icin)
├── PLAN.md                         # Implementasyon plani (faz detaylari)
└── TODO.md                         # Yapilacaklar ve tamamlananlar listesi
```

## API Endpoint'leri

| Method | Path | Aciklama | Auth |
|--------|------|----------|------|
| GET | `/api/health` | Health check | Yok |
| GET | `/api/widgets` | Widget listesi (pagination) | Evet |
| POST | `/api/widgets` | Widget olustur | Evet |
| GET | `/api/widgets/<id>` | Widget detay | Evet |
| PUT | `/api/widgets/<id>` | Widget guncelle | Evet |
| DELETE | `/api/widgets/<id>` | Widget sil | Evet |
| POST | `/api/widgets/evaluate` | Trigger evaluation | Evet |
| POST | `/api/widgets/<id>/dismiss` | Widget dismiss | Evet |
| POST | `/api/widgets/<id>/interact` | Etkilesim kaydi | Evet |
| POST | `/api/user/action` | Kullanici aksiyon kaydi | Evet |
| POST | `/api/ai/suggest-widget` | AI widget onerisi | Evet (rate limited) |
| POST | `/api/ai/generate-content` | AI icerik uretimi | Evet (rate limited) |
| GET | `/api/trends` | Trend verisi | Evet |
| POST | `/api/licenses` | Lisans olustur | Yok |
| POST | `/api/licenses/validate` | Lisans dogrula | Yok |
| GET | `/api/agent-tasks` | Agent task listesi | Evet |
| POST | `/api/agent-tasks` | Agent task kaydet | Evet |
| POST | `/api/paddle/webhook` | Paddle odeme webhook | HMAC |

## Auth Mekanizmasi

Backend iki seviyeli auth destekler:

1. **Server API Key** (`INTYX_SERVER_API_KEY`): Admin erisimi. `Authorization: Bearer <key>` header'i ile gonderilir.
2. **License Key** (`intyx_` prefix): Musteri erisimi. Aktif lisans gerektir.

`INTYX_SERVER_API_KEY` bos birakilirsa auth devre disi kalir (dev mode).

Public endpoint'ler (auth gerektirmeyen): `/api/health`, `/api/licenses`, `/api/licenses/validate`, `/api/paddle/webhook`.

## Lisans Planlari

| Plan | Widget Limiti | Fiyat |
|------|--------------|-------|
| Starter | 3 widget | Ucretsiz |
| Pro | 10 widget | Paddle uzerinden |
| Enterprise | Limitsiz | Paddle uzerinden |

## Testler

```bash
cd /path/to/intyx-dynamic-widget
python -m pytest server/tests/ -v
# 61 test (model, trigger, API, data source)
```

## Dokumantasyon

| Dokuman | Aciklama |
|---------|----------|
| [docs/API-KEYS.md](docs/API-KEYS.md) | Tum API key'ler, nereden alinir, nasil ayarlanir |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Detayli mimari, veri akisi, tasarim kararlari |
| [docs/DEPLOY-SERVER.md](docs/DEPLOY-SERVER.md) | Backend deploy (Cloud Run, Railway, Docker) |
| [docs/DEPLOY-WEB.md](docs/DEPLOY-WEB.md) | Web deploy (Vercel, Netlify, Firebase Hosting) |
| [docs/FIREBASE-SETUP.md](docs/FIREBASE-SETUP.md) | Firebase Firestore kurulumu ve security rules |
| [docs/MCP-SERVER.md](docs/MCP-SERVER.md) | MCP server kurulum ve kullanim rehberi |
| [PLAN.md](PLAN.md) | Implementasyon plani ve faz detaylari |
| [TODO.md](TODO.md) | Yapilacaklar ve tamamlananlar listesi |

## Teknoloji Yigini

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.12, Flask 3.x, Gunicorn, Firebase Admin SDK |
| Veritabani | Firebase Firestore |
| AI | Google Gemini (gemini-2.0-flash) |
| Frontend (mobil) | Flutter (Dart) — pub.dev paketi |
| Frontend (web) | React 18, Vite 5, React Router 6 |
| Odemeler | Paddle (webhook + client-side checkout) |
| MCP | Model Context Protocol (stdio transport) |
| Hata Takip | Sentry (opsiyonel) |
| Test | pytest (backend), Flutter test (frontend) |
| Deploy | Docker, Cloud Run, Vercel/Netlify |
