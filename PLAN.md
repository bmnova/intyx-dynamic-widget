# Implementation Plan - Intyx Dynamic Widget System

## Teknoloji Kararlari
- **Backend**: Python (Flask) + Firebase Admin SDK
- **Veritabani**: Firebase Firestore
- **Frontend**: Flutter - pub.dev'e yayinlanacak paket (hazir widget'lar)
- **AI Agent**: Gemini entegrasyonu (cloud uzerinden)
- **MCP**: Model Context Protocol server implementasyonu

---

## FAZE 1: Backend Core (Python/Flask)

### 1.1 Flask API Server (`server/app.py`)
- Flask uygulamasi olustur
- CORS, error handling, health check
- Blueprint yapisi ile modular routing

### 1.2 Firebase Firestore Entegrasyonu (`server/firebase_client.py`)
- Firebase Admin SDK ile Firestore baglantisi
- Collection yapisi:
  - `widgets` - Widget tanimlari
  - `trigger_rules` - Tetikleme kurallari
  - `user_states` - Kullanici durumlari (dismissed, interactions)
  - `data_cache` - Data source cache (weather, news, horoscope)

### 1.3 API Endpoint'leri (`server/routes/`)
- `GET /api/widgets` - Aktif widget listesi (context'e gore filtrelenmis)
- `POST /api/widgets/evaluate` - Trigger evaluation (context gonder, uygun widget'lari al)
- `POST /api/widgets/{id}/dismiss` - Widget dismiss
- `POST /api/widgets/{id}/interact` - Widget interaction kaydi
- `GET /api/widgets/{id}` - Tekil widget detay
- `POST /api/user/action` - Kullanici aksiyon kaydi
- `GET /api/health` - Health check

### 1.4 Data Source Scheduler (`server/scheduler.py`)
- Periyodik data polling (weather, news, horoscope)
- Async task runner
- Firestore'a cache yazimi

---

## FAZE 2: MCP Server

### 2.1 MCP Protocol Implementation (`server/mcp/`)
- MCP server (stdio transport)
- Tool tanimlari:
  - `create_widget` - Yeni widget tanimla
  - `list_widgets` - Widget'lari listele
  - `update_widget` - Widget guncelle
  - `delete_widget` - Widget sil
  - `create_trigger_rule` - Trigger kurali olustur
  - `evaluate_triggers` - Manuel trigger evaluation
  - `get_data_sources` - Mevcut data source durumlarini gor
- Resource tanimlari:
  - `widget://list` - Tum widget'lar
  - `widget://{id}` - Tekil widget
  - `datasource://weather` - Guncel hava durumu
  - `datasource://news` - Guncel haberler

---

## FAZE 3: Gemini AI Agent Entegrasyonu

### 3.1 Gemini Client (`server/ai/gemini_client.py`)
- Google Generative AI SDK entegrasyonu
- Widget icerigi onerisi (context'e gore)
- Trigger kural onerisi
- Dogal dil ile widget olusturma

### 3.2 AI-Powered Endpoints
- `POST /api/ai/suggest-widget` - Context'e gore widget onerisi
- `POST /api/ai/generate-content` - Widget icerigi uretimi
- Gemini MCP tool olarak da erisim

---

## FAZE 4: Flutter Widget Paketi

### 4.1 Paket Yapisi (`flutter_client/`)
- `pubspec.yaml` - Paket tanimlari, bagimliliklar
- Paket adi: `intyx_dynamic_widget`
- Min SDK, Firebase dependencies, http

### 4.2 Widget Catalog & JSON-Driven Mimari

**Temel Prensip:** Agent hangi widget'in gosterilecegine karar verir ve JSON response doner.
Flutter paketi bu JSON'i parse edip dogru widget'i render eder.

#### Widget Catalog Dosyasi (`lib/catalog/widget_catalog.json`)
Agent'in gorebilecegi, tum widget tiplerini ve parametrelerini tanimlayan JSON schema:

```json
{
  "catalog_version": "1.0.0",
  "widgets": [
    {
      "type": "title_subtitle_image",
      "description": "Baslik, alt baslik ve resim iceren kart",
      "params": {
        "title":      { "type": "string", "required": true,  "description": "Ana baslik" },
        "subtitle":   { "type": "string", "required": false, "description": "Alt baslik" },
        "image_url":  { "type": "string", "required": true,  "description": "Resim URL" },
        "image_fit":  { "type": "enum",   "values": ["cover","contain","fill"], "default": "cover" }
      }
    },
    {
      "type": "clickable_image_link",
      "description": "Tiklanabilir resim, baslik ve yonlendirme linki",
      "params": {
        "title":      { "type": "string", "required": true },
        "image_url":  { "type": "string", "required": true },
        "link_url":   { "type": "string", "required": true,  "description": "Tiklaninca acilacak URL" },
        "link_text":  { "type": "string", "required": false, "description": "Link gosterim metni" }
      }
    },
    {
      "type": "hero_image",
      "description": "Tam genislikte hero resim, overlay baslik ve CTA butonu",
      "params": {
        "title":        { "type": "string", "required": true },
        "image_url":    { "type": "string", "required": true },
        "button_text":  { "type": "string", "required": false },
        "button_action":{ "type": "string", "required": false, "description": "deep_link veya URL" }
      }
    },
    {
      "type": "icon_text_action",
      "description": "Ikon, baslik, aciklama ve aksiyon butonu",
      "params": {
        "icon":         { "type": "string", "required": true,  "description": "Material icon adi" },
        "title":        { "type": "string", "required": true },
        "description":  { "type": "string", "required": false },
        "action_text":  { "type": "string", "required": false },
        "action_url":   { "type": "string", "required": false }
      }
    },
    {
      "type": "countdown_banner",
      "description": "Geri sayim zamanlayici ile kampanya banner'i",
      "params": {
        "title":       { "type": "string",   "required": true },
        "end_time":    { "type": "datetime", "required": true, "description": "ISO 8601 bitis zamani" },
        "button_text": { "type": "string",   "required": false },
        "button_action":{ "type": "string",  "required": false }
      }
    },
    {
      "type": "carousel",
      "description": "Yatay kaydirmali coklu icerik karti",
      "params": {
        "title":  { "type": "string", "required": false },
        "items":  {
          "type": "array",
          "required": true,
          "item_params": {
            "image_url":   { "type": "string", "required": true },
            "title":       { "type": "string", "required": false },
            "description": { "type": "string", "required": false },
            "link_url":    { "type": "string", "required": false }
          }
        }
      }
    },
    {
      "type": "promotional",
      "description": "Kampanya/promosyon karti - ozel tasarim",
      "params": {
        "title":        { "type": "string", "required": true },
        "description":  { "type": "string", "required": false },
        "image_url":    { "type": "string", "required": false },
        "badge_text":   { "type": "string", "required": false, "description": "Rozet metni (orn: %50 Indirim)" },
        "action_url":   { "type": "string", "required": false }
      }
    },
    {
      "type": "contextual",
      "description": "Baglamsal bilgi karti (hava durumu, burc vs.)",
      "params": {
        "title":       { "type": "string", "required": true },
        "content":     { "type": "string", "required": true },
        "icon":        { "type": "string", "required": false },
        "source":      { "type": "string", "required": false, "description": "Veri kaynagi etiketi" }
      }
    },
    {
      "type": "informational",
      "description": "Bilgilendirme/duyuru karti",
      "params": {
        "title":       { "type": "string", "required": true },
        "message":     { "type": "string", "required": true },
        "severity":    { "type": "enum", "values": ["info","warning","success","error"], "default": "info" }
      }
    },
    {
      "type": "functional",
      "description": "Aksiyon odakli kart - buton(lar) ve form alanlari",
      "params": {
        "title":   { "type": "string", "required": true },
        "actions": {
          "type": "array",
          "required": true,
          "item_params": {
            "label":  { "type": "string", "required": true },
            "action": { "type": "string", "required": true, "description": "deep_link, URL veya callback_id" },
            "style":  { "type": "enum", "values": ["primary","secondary","text"], "default": "primary" }
          }
        }
      }
    }
  ],
  "common_params": {
    "dismissible":    { "type": "bool",   "default": true,  "description": "Kapatilabilir mi?" },
    "priority":       { "type": "int",    "default": 0,     "description": "Gosterim onceligi (yuksek = once)" },
    "ttl_seconds":    { "type": "int",    "default": null,  "description": "Yasam suresi (null = sinirsiz)" },
    "theme_override": { "type": "object", "default": null,  "description": "Ozel tema (bg_color, text_color, border_radius)" }
  }
}
```

#### Agent JSON Response Formati
Agent su formatta response doner:

```json
{
  "widgets": [
    {
      "id": "w_abc123",
      "type": "title_subtitle_image",
      "params": {
        "title": "Istanbul'da Bugun",
        "subtitle": "Parcali bulutlu, 18°C",
        "image_url": "https://cdn.example.com/weather/cloudy.png"
      },
      "common": {
        "dismissible": true,
        "priority": 10,
        "ttl_seconds": 3600
      }
    },
    {
      "id": "w_def456",
      "type": "countdown_banner",
      "params": {
        "title": "Yaz Indirimi Basliyor!",
        "end_time": "2025-06-15T23:59:59Z",
        "button_text": "Firsatlari Gor",
        "button_action": "app://deals"
      },
      "common": {
        "priority": 20
      }
    }
  ]
}
```

#### Widget Registry & Resolver (`lib/core/`)

- **`widget_registry.dart`** - Widget type -> Flutter Widget eslestirme registry'si
  ```dart
  // Ornek kullanim:
  WidgetRegistry.register('title_subtitle_image', TitleSubtitleImageCard.fromJson);
  WidgetRegistry.register('countdown_banner', CountdownBannerCard.fromJson);
  ```

- **`widget_resolver.dart`** - JSON response'u parse edip Flutter widget listesine ceviren resolver
  ```dart
  // Agent response JSON geldi -> Widget listesi
  final widgets = WidgetResolver.resolve(agentResponseJson);
  // -> [TitleSubtitleImageCard(...), CountdownBannerCard(...)]
  ```

- **`catalog_provider.dart`** - widget_catalog.json'i okuyup agent'a sunmak icin
  ```dart
  // Agent'a gondermek icin catalog JSON'ini dondurur
  final catalogJson = CatalogProvider.getCatalog();
  ```

**Akis:**
```
1. App baslarken -> CatalogProvider catalog'u yukler
2. Backend/Agent'a istek atilirken catalog da gonderilir (veya agent zaten biliyor)
3. Agent karar verir: "title_subtitle_image widget'ini su parametrelerle goster"
4. Agent JSON response doner
5. WidgetResolver JSON'i parse eder
6. WidgetRegistry'den dogru Flutter widget'i bulur
7. Widget params ile olusturulur ve ekranda gosterilir
```

### 4.3 Dart Modelleri (`lib/models/`)
- `widget_definition.dart` - WidgetDefinition, WidgetContent, WidgetAction
- `widget_response.dart` - Agent JSON response modeli
- `trigger_context.dart` - TriggerContext (client-side)

### 4.4 Service Katmani (`lib/services/`)
- `widget_service.dart` - Backend API ile haberlesme
- `firebase_service.dart` - Firestore realtime listener'lar

### 4.5 Hazir Widget'lar (`lib/widgets/`)
Her widget'in `fromJson(Map<String, dynamic> params)` factory constructor'i olacak.

#### A) Dinamik/Trigger Widget'lari
- `DynamicWidgetContainer` - Ana wrapper, WidgetResolver ile JSON'dan widget listesi olusturur
- `PromotionalWidget` - type: `promotional`
- `ContextualWidget` - type: `contextual`
- `InformationalWidget` - type: `informational`
- `FunctionalWidget` - type: `functional`
- Her widget: dismiss, interact callback'leri, animasyon

#### B) UI Widget'lari (`lib/widgets/ui/`)

- **`TitleSubtitleImageCard`** - type: `title_subtitle_image`
  ```
  ┌─────────────────────┐
  │  [  Resim  ]        │
  │  Baslik              │
  │  Alt baslik          │
  └─────────────────────┘
  ```

- **`ClickableImageLinkCard`** - type: `clickable_image_link`
  ```
  ┌─────────────────────┐
  │  Baslik              │
  │  [ Tiklanabilir Img ]│
  │  Link metni          │
  └─────────────────────┘
  ```

- **`HeroImageCard`** - type: `hero_image`
  ```
  ┌─────────────────────┐
  │   [ Hero Image ]     │
  │      Baslik          │
  │      Buton           │
  └─────────────────────┘
  ```

- **`IconTextActionCard`** - type: `icon_text_action`
  ```
  ┌─────────────────────┐
  │  IC  Baslik     [>]  │
  │      Aciklama        │
  └─────────────────────┘
  ```

- **`CountdownBannerCard`** - type: `countdown_banner`
  ```
  ┌─────────────────────┐
  │  02:15:30            │
  │  Kampanya basligi    │
  │  [ Katil ]           │
  └─────────────────────┘
  ```

- **`CarouselCard`** - type: `carousel`
  ```
  ┌─────────────────────┐
  │  < [Img1][Img2] >   │
  │  Baslik              │
  │  Aciklama            │
  └─────────────────────┘
  ```

### 4.6 Kullanim Ornegi (`example/`)
- Ornek Flutter uygulamasi
- Entegrasyon dokumantasyonu

---

## FAZE 5: Testler

### 5.1 Backend Testleri (`server/tests/`)
- Model testleri
- Trigger engine testleri
- API endpoint testleri (Flask test client)
- Data source testleri

### 5.2 Flutter Testleri (`flutter_client/test/`)
- Model serialization testleri
- Widget render testleri
- Service mock testleri

---

## Dosya Yapisi (Hedef)

```
intyx-dynamic-widget/
├── server/
│   ├── app.py                    # Flask app + blueprint registration
│   ├── config.py                 # (mevcut)
│   ├── models.py                 # (mevcut)
│   ├── firebase_client.py        # Firestore client
│   ├── scheduler.py              # Data source polling
│   ├── requirements.txt          # (guncellenecek: + google-generativeai, mcp)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── widgets.py            # Widget API endpoints
│   │   └── ai.py                 # AI endpoints
│   ├── ai/
│   │   ├── __init__.py
│   │   └── gemini_client.py      # Gemini SDK wrapper
│   ├── data_sources/             # (mevcut)
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py             # MCP server implementation
│   ├── triggers/                 # (mevcut)
│   └── tests/
│       ├── test_models.py
│       ├── test_triggers.py
│       ├── test_api.py
│       └── test_data_sources.py
└── flutter_client/
    ├── pubspec.yaml
    ├── lib/
    │   ├── intyx_dynamic_widget.dart   # Library export
    │   ├── catalog/
    │   │   └── widget_catalog.json     # Widget catalog - agent bunu gorur
    │   ├── core/
    │   │   ├── widget_registry.dart    # type -> Widget eslestirme
    │   │   ├── widget_resolver.dart    # JSON -> Widget listesi
    │   │   └── catalog_provider.dart   # Catalog JSON okuma/sunma
    │   ├── models/
    │   │   ├── widget_definition.dart
    │   │   ├── widget_response.dart    # Agent JSON response modeli
    │   │   └── trigger_context.dart
    │   ├── services/
    │   │   ├── widget_service.dart
    │   │   └── firebase_service.dart
    │   └── widgets/
    │       ├── dynamic_widget_container.dart
    │       ├── promotional_widget.dart
    │       ├── contextual_widget.dart
    │       ├── informational_widget.dart
    │       ├── functional_widget.dart
    │       └── ui/
    │           ├── title_subtitle_image_card.dart
    │           ├── clickable_image_link_card.dart
    │           ├── hero_image_card.dart
    │           ├── icon_text_action_card.dart
    │           ├── countdown_banner_card.dart
    │           └── carousel_card.dart
    ├── example/
    │   └── lib/main.dart
    └── test/
        ├── models_test.dart
        └── widgets_test.dart
```

## Uygulama Sirasi
1. Backend Core (Flask API + Firebase)
2. MCP Server
3. Gemini AI Agent
4. Flutter Widget Paketi
5. Testler
