# Mimari Dokumani

Intyx Dynamic Widget System'in detayli mimari yapisi, veri akisi ve tasarim kararlari.

---

## Genel Bakis

Sistem 4 ana bilesenden olusur:

```
+-------------------+     +-------------------+     +------------------+
|  Flutter Client   |     |   Web Dashboard   |     |    MCP Client    |
|  (mobil app SDK)  |     |   (React/Vite)    |     | (Cursor/Claude)  |
+--------+----------+     +--------+----------+     +--------+---------+
         |                         |                          |
         |   REST API (JSON)       |   REST API               | stdio (MCP)
         |                         |                          |
+--------v-------------------------v--------------------------v---------+
|                        Python Backend (Flask)                         |
|                                                                      |
|  +-------------+  +-----------+  +----------+  +------------------+  |
|  |   Routes    |  |  Trigger  |  |   Data   |  |   Gemini AI      |  |
|  |  (6 BP)     |  |  Engine   |  |  Sources |  |  (suggest/gen)   |  |
|  +------+------+  +-----+-----+  +----+-----+  +--------+---------+  |
|         |               |              |                 |            |
|  +------v---------------v--------------v-----------------v---------+  |
|  |                    Firebase Firestore                           |  |
|  |  widgets | trigger_rules | licenses | agent_tasks | data_cache  |  |
|  +-------------------------------------------------------------+  |
+-------------------------------------------------------------------+
```

---

## Backend (server/)

### Flask Application (`app.py`)

```
create_app()
  ├── validate_config()        # Zorunlu env kontrol (fail fast)
  ├── Sentry init              # Opsiyonel hata takip
  ├── CORS                     # Cross-origin izin
  ├── Rate Limiter             # 200/saat genel, 30/dk AI
  ├── Auth Middleware           # before_request hook
  │   ├── PUBLIC_PATHS         # /api/health, /api/licenses, vb.
  │   ├── Server API Key       # INTYX_SERVER_API_KEY → admin
  │   └── License Key          # intyx_xxx → aktif lisans
  ├── Blueprint Registration
  │   ├── widgets_bp           # /api/widgets/*
  │   ├── ai_bp                # /api/ai/*
  │   ├── licenses_bp          # /api/licenses/*
  │   ├── agent_tasks_bp       # /api/agent-tasks/*
  │   ├── trends_bp            # /api/trends/*
  │   └── paddle_bp            # /api/paddle/*
  └── Error Handlers           # 404, 429, 500
```

### Routes (`server/routes/`)

| Blueprint | Prefix | Endpoint'ler |
|-----------|--------|-------------|
| `widgets_bp` | `/api` | GET/POST/PUT/DELETE `/widgets`, POST `/widgets/evaluate`, `/widgets/<id>/dismiss`, `/widgets/<id>/interact`, `/user/action` |
| `ai_bp` | `/api/ai` | POST `/suggest-widget`, POST `/generate-content` |
| `licenses_bp` | `/api/licenses` | POST `/`, POST `/validate` |
| `agent_tasks_bp` | `/api/agent-tasks` | GET `/`, POST `/` |
| `trends_bp` | `/api/trends` | GET `/` |
| `paddle_bp` | `/api/paddle` | POST `/webhook` |

### Firebase Client (`firebase_client.py`)

Thread-safe Firestore istemcisi. Double-check locking ile tek seferlik init.

```
firebase_client
  ├── Widget Operations    → get_widgets, get_widget, create_widget, update_widget, delete_widget
  ├── Trigger Rules        → get_trigger_rules, create_trigger_rule, delete_trigger_rule
  ├── User State           → get_user_state, dismiss_widget, record_interaction, record_user_action
  │   └── (transactional)   → Array update'ler race condition'siz
  ├── Data Cache           → cache_data, get_cached_data, delete_cached_data
  ├── License Operations   → create_license, get_license, deactivate_license_by_paddle_customer, count_widgets_for_license
  │   └── (cache-first)     → Oncelik: data_cache → Firestore → cache'e yaz
  └── Agent Tasks          → get_agent_tasks, save_agent_tasks
      └── (cache-first)     → Ayni cache-first pattern
```

### Trigger Engine (`server/triggers/`)

Widget'larin ne zaman gosterilecegine karar veren kural motoru.

```
TriggerEngine.evaluate(context, trigger_rules, user_state)
  ├── SeasonalCondition      → Tarih/sezon eslestirme (halloween, yilbasi, vb.)
  ├── WeatherMatchCondition  → Hava durumu eslestirme (sicaklik, nem, condition)
  ├── UserActionCondition    → Kullanici davranisi (N kez X aksiyonu yapmissa)
  └── DeveloperParamCondition → Gelistirici parametreleri (key-value eslestirme)
```

### Data Sources (`server/data_sources/`)

Pub/Sub pattern ile calisir. Scheduler periyodik olarak poll eder, Firestore'a cache yazar.

| Source | API | Polling | Aciklama |
|--------|-----|---------|----------|
| `WeatherSource` | OpenWeatherMap | 5 dk | Sehir bazli hava durumu |
| `NewsSource` | NewsAPI.org | 10 dk | Ulke bazli guncel haberler |
| `HoroscopeSource` | Gemini AI | 1 saat | 12 burc tek batch'te |
| `TrendSource` | Twitter/X | 15 dk | Bolgesel trend verileri |

### AI (`server/ai/`)

```
GeminiClient (singleton via get_gemini_client())
  ├── suggest_widgets(context)    → Widget onerisi (JSON array doner)
  ├── generate_content(type, ctx) → Widget parametreleri uretir
  └── Model: GEMINI_MODEL_NAME   → Varsayilan: gemini-2.0-flash
```

---

## MCP Server (`server/mcp/`)

### Tool Definitions (`tool_definitions.py`)

Single source of truth. Her tool:
- `name`: Tool adi
- `description`: Aciklama
- `schema`: JSON Schema (input parametreleri)
- `agent_visible`: Gemini agent'in gorup goremeyecegi (True/False)

### Server (`server.py`)

Handler registry pattern:
```python
HANDLERS = {
    "create_widget": widget_handlers.handle_create_widget,
    "get_current_weather": weather_handlers.handle_get_current_weather,
    "ask": _handle_ask,
    # ... 20 handler
}
```

Global error wrapper: Herhangi bir handler exception firlatirsa, sunucu dusmez — hata mesaji doner.

### Agent (`agent.py`)

```
run_ask(query)
  ├── tool_definitions.py'dan agent_visible tool'lari al
  ├── Gemini function declarations olustur (auto-generated)
  ├── MAX_TURNS=10 agentic loop
  │   ├── Gemini'ye sor
  │   ├── function_call varsa → handler'i cagir
  │   ├── Sonucu Gemini'ye geri gonder
  │   └── Tekrarla (veya text response gelirse bitir)
  └── Final text response donder
```

---

## Flutter SDK (`flutter_client/`)

### Veri Akisi

```
App Baslatma:
  registerDefaultWidgets() → WidgetRegistry'ye 16 tip kaydet
  IntyxInit.initialize()   → Firebase, services init

Widget Gosterme:
  DynamicWidgetContainer(triggerContext)
    ├── WidgetService.evaluate(context)  → Backend'e istek
    ├── Backend: TriggerEngine + AI      → JSON response
    ├── WidgetResolver.resolve(json)     → Type'a gore parse
    ├── WidgetRegistry.build(type)       → Flutter Widget olustur
    └── ResponsiveWidgetWrapper(layout)  → Boyut/padding wrap
```

### Widget Katalogu (16 tip)

| Tip | Widget | Aciklama |
|-----|--------|----------|
| `title_subtitle_image` | TitleSubtitleImageCard | Baslik + alt baslik + resim |
| `clickable_image_link` | ClickableImageLinkCard | Tiklanabilir resim + link |
| `hero_image` | HeroImageCard | Full-width hero + CTA |
| `icon_text_action` | IconTextActionCard | Ikon + metin + aksiyon |
| `countdown_banner` | CountdownBannerCard | Geri sayim zamanlayici |
| `carousel` | CarouselCard | Yatay kaydirmali kartlar |
| `promotional` | PromotionalWidget | Kampanya/promosyon |
| `contextual` | ContextualWidget | Baglamsal bilgi (hava, burc) |
| `informational` | InformationalWidget | Bilgilendirme/duyuru |
| `functional` | FunctionalWidget | Aksiyon odakli (butonlar) |
| `banner` | BannerCard | Genel banner |
| `poll` | PollCard | Anket/oylama |
| `rating` | RatingCard | Yildiz puanlama |
| `profile` | ProfileCard | Profil karti |
| `progress` | ProgressCard | Ilerleme gostergesi |
| `social_proof` | SocialProofCard | Sosyal kanit (referans) |

### Layout Sistemi

`ResponsiveWidgetWrapper` common params'tan gelen layout config'e gore widget'i sararlar:
- `expand: true` (varsayilan) → Parent genisligine yayil
- `width/height` → Sabit boyut
- `max_width/max_height` → Constraint
- `aspect_ratio` → Genislige gore yukseklik
- `padding/margin` → Edge insets (CSS sirasinda degil: [top, right, bottom, left])

---

## Web Dashboard (`web/`)

React 18 + Vite 5 + React Router 6 ile tek sayfa uygulama.

### Sayfa Akisi

```
Landing (/) → Pricing (/pricing) → Lisans al → Dashboard (/dashboard)
                                                    |
                                        +-----------+-----------+
                                        |                       |
                                Widget Studio              Agent Tasks
                              (/widget-studio)          (/agent-tasks)
```

### Widget Studio (3 Adim)

1. **Widget Sec:** 16 tipten multi-select
2. **Prompt Yaz:** Agent task tanimla (veya hazir sablonlardan sec)
3. **Onizle:** Widget preview + agent task olarak kaydet

---

## Odeme Akisi (Paddle)

```
Web: Pricing sayfasi
  → Paddle checkout ac (client-side)
  → Kullanici odeme yapar
  → Paddle → POST /api/paddle/webhook
     ├── HMAC-SHA256 imza dogrula
     ├── transaction.completed → create_license(plan, paddle_customer_id)
     └── subscription.canceled → deactivate_license_by_paddle_customer()
```

### Lisans Kontrol

Widget olusturma sirasinda plan limiti kontrol edilir:
```
POST /api/widgets
  → count_widgets_for_license(api_key)
  → plan.widget_limit ile karsilastir
  → limit asildiysa 403 dondur
```

---

## Guvenlik

| Katman | Mekanizma |
|--------|-----------|
| API Auth | Server key (admin) + License key (musteri) |
| Rate Limiting | 200/saat genel, 30/dk AI endpoint'leri |
| Webhook | HMAC-SHA256 imza dogrulama (Paddle) |
| Firestore | Security rules (client-side erisim kontrolu) |
| Error Tracking | Sentry (opsiyonel) |
| Input Validation | Widget type/params schema kontrolu |
| Transactional | Array update'ler race condition'siz |
| Fail Fast | Zorunlu env'ler eksikse startup'ta exit |

---

## Konfigurasyon

Tum konfigur degerleri `server/config.py` dosyasinda tanimlidir. Degerler environment variable'lardan okunur, `.env` dosyasindan otomatik yuklenr (python-dotenv).

Detayli liste: [API-KEYS.md](./API-KEYS.md)
