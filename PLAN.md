# Implementation Plan - Intyx Dynamic Widget System

## Durum Ozeti

| Faz | Durum | Aciklama |
|-----|-------|----------|
| Faz 1: Backend Core | Tamamlandi | Flask API, Firebase, Scheduler |
| Faz 2: MCP Server | Tamamlandi | 20 tool, handler registry, Gemini agent |
| Faz 3: Gemini AI Agent | Tamamlandi | Suggest, generate, ask (tool orchestration) |
| Faz 4: Flutter Widget Paketi | Tamamlandi | 15+ widget tipi, JSON-driven, responsive |
| Faz 5: Testler | Tamamlandi | 61 test (model, trigger, API, data source) |
| Faz 6: Web Dashboard | Tamamlandi | Widget Studio, Agent Tasks, Pricing |
| Faz 7: Guvenlik & Odemeler | Tamamlandi | Auth middleware, Paddle webhook, Sentry |

---

## Teknoloji Kararlari

- **Backend**: Python 3.12 (Flask) + Firebase Admin SDK + Gunicorn
- **Veritabani**: Firebase Firestore
- **Frontend (mobil)**: Flutter — pub.dev'e yayinlanacak paket (15+ hazir widget)
- **Frontend (web)**: React 18 + Vite 5 — dashboard, pricing, widget studio
- **AI**: Gemini (gemini-2.0-flash) — widget onerisi, icerik uretimi, agentic orchestration
- **MCP**: Model Context Protocol server (stdio transport) — Cursor/Claude Desktop entegrasyonu
- **Odemeler**: Paddle — webhook (HMAC-SHA256) + client-side checkout
- **Hata Takip**: Sentry (opsiyonel)

---

## FAZ 1: Backend Core (Tamamlandi)

### 1.1 Flask API Server (`server/app.py`)
- [x] Flask uygulamasi + CORS + error handling + health check
- [x] Blueprint yapisi ile modular routing (6 blueprint)
- [x] Auth middleware (server key + license key, dual-level)
- [x] Rate limiting (Flask-Limiter: genel 200/saat, AI 30/dakika)
- [x] Sentry error tracking (opsiyonel, SENTRY_DSN ile)

### 1.2 Firebase Firestore Entegrasyonu (`server/firebase_client.py`)
- [x] Firebase Admin SDK ile Firestore baglantisi (thread-safe, double-check locking)
- [x] Collection yapisi:
  - `widgets` — Widget tanimlari
  - `trigger_rules` — Tetikleme kurallari
  - `user_states` — Kullanici durumlari (dismissed, interactions, user_actions)
  - `data_cache` — Data source cache
  - `licenses` — Lisans kayitlari (Firestore-backed)
  - `agent_tasks` — Agent task/persona kayitlari (Firestore-backed)
- [x] Transactional array updates (race condition onleme)
- [x] Cache-first reads with Firestore fallback

### 1.3 API Endpoint'leri (`server/routes/`)
- [x] Widget CRUD: list, create, get, update, delete (pagination destekli)
- [x] Trigger evaluation, dismiss, interact, user action
- [x] AI: suggest-widget, generate-content (rate limited)
- [x] Licenses: create, validate
- [x] Agent tasks: get, save
- [x] Trends: get
- [x] Paddle webhook: transaction.completed, subscription.canceled
- [x] Plan limit enforcement (starter=3, pro=10, enterprise=unlimited)

### 1.4 Data Source Scheduler (`server/scheduler.py`)
- [x] Periyodik data polling (weather, news, horoscope, trends)
- [x] Exponential backoff on API errors
- [x] Firestore'a cache yazimi

### 1.5 Data Sources (`server/data_sources/`)
- [x] `weather_source.py` — OpenWeatherMap API entegrasyonu
- [x] `news_source.py` — NewsAPI.org entegrasyonu (gercek veri)
- [x] `horoscope_source.py` — Gemini AI ile burc yorumu (12 burc tek batch)
- [x] `trend_source.py` — Twitter/X trend verisi

---

## FAZ 2: MCP Server (Tamamlandi)

### 2.1 MCP Protocol Implementation (`server/mcp/`)
- [x] MCP server (stdio transport) — handler registry pattern
- [x] 20 tool tanimi — single source of truth (`tool_definitions.py`)
- [x] Domain-based handler modules:
  - `widget_handlers.py` — Widget CRUD + triggers
  - `weather_handlers.py` — OpenWeatherMap (current, forecast, by_coords)
  - `holiday_handlers.py` — Tatil/ozel gunler
  - `trend_handlers.py` — Viral trendler
  - `ai_handlers.py` — Data sources + AI suggest
- [x] Global error wrapper (`call_tool` hicbir handler sunucuyu dusuremiyor)
- [x] Gemini agent auto-generated declarations (tool_definitions.py'dan)

---

## FAZ 3: Gemini AI Agent Entegrasyonu (Tamamlandi)

### 3.1 Gemini Client (`server/ai/gemini_client.py`)
- [x] Google Generative AI SDK entegrasyonu
- [x] Singleton pattern (`get_gemini_client()`)
- [x] Widget onerisi (context'e gore)
- [x] Widget icerik uretimi
- [x] Configurable model name (`GEMINI_MODEL_NAME`, varsayilan: gemini-2.0-flash)

### 3.2 Agent (`server/mcp/agent.py`)
- [x] `run_ask()` function — dogal dilde soru, Gemini tool orchestration
- [x] MAX_TURNS=10 agentic loop
- [x] Auto-generated function declarations from `tool_definitions.py`
- [x] `agent_visible` flag ile sadece agent'a acik tool'lar filtrelenir

---

## FAZ 4: Flutter Widget Paketi (Tamamlandi)

### 4.1 Paket Yapisi (`flutter_client/`)
- [x] `pubspec.yaml` — Paket tanimlari, bagimliliklar
- [x] Paket adi: `intyx_dynamic_widget` (v0.1.0)
- [x] Library export: `intyx_dynamic_widget.dart`
- [x] `registerDefaultWidgets()` — tek satirla tum widget'lari kaydet

### 4.2 Widget Catalog & JSON-Driven Mimari
- [x] `widget_catalog.json` — 16 widget tipi tanimli
- [x] Agent JSON response formati (id, type, params, common)
- [x] Common params: dismissible, priority, ttl_seconds, theme_override, layout
- [x] Layout: width, height, max_width, max_height, padding, margin, expand, aspect_ratio

### 4.3 Core
- [x] `WidgetRegistry` — type -> Widget eslestirme (register/resolve pattern)
- [x] `WidgetResolver` — JSON array -> Flutter Widget listesi
- [x] `CatalogProvider` — widget_catalog.json okuma/sunma
- [x] `IntyxInit` — SDK baslatma (firebaseProjectId, catalogJsonUrl, widgetServiceBaseUrl)
- [x] `ResponsiveWidgetWrapper` — Layout/boyut/padding/margin/aspect_ratio wrapper

### 4.4 Hazir Widget'lar (15+)
Kategori widget'lari:
- [x] `PromotionalWidget`, `ContextualWidget`, `InformationalWidget`, `FunctionalWidget`
- [x] `DynamicWidgetContainer` — Ana wrapper, WidgetResolver ile JSON'dan rendering

UI widget'lari (12 adet):
- [x] BannerCard, CarouselCard, ClickableImageLinkCard, CountdownBannerCard
- [x] HeroImageCard, IconTextActionCard, PollCard, ProfileCard
- [x] ProgressCard, RatingCard, SocialProofCard, TitleSubtitleImageCard

### 4.5 Services
- [x] `WidgetService` — Backend API haberlesme
- [x] `FirebaseService` — Firestore realtime listener

### 4.6 Ornek Uygulama (`example/`)
- [x] Flutter ornek uygulama — DynamicWidgetContainer kullanimi
- [x] Ornek agent JSON ile widget rendering

---

## FAZ 5: Testler (Tamamlandi)

### 5.1 Backend Testleri (`server/tests/`)
- [x] `test_models.py` — Model serialization/deserialization
- [x] `test_triggers.py` — Trigger engine ve condition testleri
- [x] `test_api.py` — 28 API endpoint testi:
  - Widget CRUD (7 test)
  - Trigger evaluation (2 test)
  - User actions (2 test)
  - License endpoints (4 test)
  - Agent task endpoints (4 test)
  - Paddle webhook (3 test)
  - AI endpoints (3 test)
  - Plan enforcement (2 test)
  - Health check (1 test)
- [x] `test_data_sources.py` — Weather, News, Horoscope, Trend source testleri
- [x] **Toplam: 61 test, hepsi geciyor**

---

## FAZ 6: Web Dashboard (Tamamlandi)

- [x] `Landing.jsx` — Ana sayfa (SEO meta tags, Open Graph, Twitter card)
- [x] `Dashboard.jsx` — Kontrol paneli (quick action cards)
- [x] `WidgetStudio.jsx` — 3-adimli widget olusturma (sec -> prompt -> onizle)
- [x] `AgentTasks.jsx` — Agent task/persona yonetimi (CRUD)
- [x] `Pricing.jsx` — Plan/fiyat sayfasi (Paddle checkout entegrasyonu)
- [x] `ProtectedRoute.jsx` — API key + dev mode guard
- [x] `NotFound.jsx` — 404 sayfasi
- [x] `Toast.jsx` — Bildirim bileşeni
- [x] `Navbar.jsx` — Navigasyon (Landing, Dashboard, Studio, Tasks, Pricing)

---

## FAZ 7: Guvenlik & Odemeler (Tamamlandi)

- [x] Auth middleware (server key + license key, dual-level)
- [x] Public paths: /api/health, /api/licenses, /api/licenses/validate, /api/paddle/webhook
- [x] Rate limiting (genel: 200/saat, AI: 30/dakika, configurable)
- [x] Paddle webhook handler (HMAC-SHA256 signature verification)
- [x] Otomatik lisans olusturma (transaction.completed event)
- [x] Lisans iptal (subscription.canceled event)
- [x] Plan limit enforcement (widget create'te limit kontrol)
- [x] Sentry error tracking (opsiyonel, SENTRY_DSN ile)
- [x] Firestore security rules (`firestore.rules`)
- [x] Firestore composite indexes (`firestore.indexes.json`)

---

## Gelecek Iyilestirmeler

### Kritik
- [ ] `INTYX_SERVER_API_KEY` production'da aktif et
- [ ] Flutter SDK'da lisans dogrulama (widget renderer'da server-side kontrol)

### Onemli
- [ ] SDK analytics (widget impression/interaction event tracking)
- [ ] Offline caching (Flutter — son widget state'i local'de tut)
- [ ] OpenAPI/Swagger API dokumantasyonu
- [ ] CI/CD pipeline (GitHub Actions — test + deploy)
- [ ] `.env.example` dosyalarini tum yeni key'lerle guncelle

### Guzel Olur
- [ ] Landing page'de interaktif widget demo
- [ ] Accessibility iyilestirmeleri (aria-label, keyboard navigation)
- [ ] Widget A/B testing mekanizmasi
- [ ] Multi-language widget content support
- [ ] Admin dashboard (lisans yonetimi, analytics)
