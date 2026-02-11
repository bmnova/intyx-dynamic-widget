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

### 4.2 Dart Modelleri (`lib/models/`)
- `widget_definition.dart` - WidgetDefinition, WidgetContent, WidgetAction
- `trigger_context.dart` - TriggerContext (client-side)

### 4.3 Service Katmani (`lib/services/`)
- `widget_service.dart` - Backend API ile haberlesme
- `firebase_service.dart` - Firestore realtime listener'lar

### 4.4 Hazir Widget'lar (`lib/widgets/`)
- `DynamicWidgetContainer` - Ana wrapper, widget listesini gosterir
- `PromotionalWidget` - Kampanya/promosyon karti
- `ContextualWidget` - Baglamsal bilgi karti (hava, burc vs.)
- `InformationalWidget` - Bilgilendirme/duyuru karti
- `FunctionalWidget` - Aksiyon odakli kart (buton, form vs.)
- Her widget: dismiss, interact callback'leri, animasyon

### 4.5 Kullanim Ornegi (`example/`)
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
    │   ├── models/
    │   │   ├── widget_definition.dart
    │   │   └── trigger_context.dart
    │   ├── services/
    │   │   ├── widget_service.dart
    │   │   └── firebase_service.dart
    │   └── widgets/
    │       ├── dynamic_widget_container.dart
    │       ├── promotional_widget.dart
    │       ├── contextual_widget.dart
    │       ├── informational_widget.dart
    │       └── functional_widget.dart
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
