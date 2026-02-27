# Intyx Dynamic Widget System

> **Experimental project.** This is an early-stage open-source system under active development.
> APIs and widget schemas may change between versions. Not recommended for production apps without thorough testing.

A signal-driven content selection system for Flutter apps.
Predefined widget templates are dynamically populated based on live context signals — without shipping a new app build.

---

## What it solves

Showing different content to different users in a mobile app usually means one of two things:

1. Hardcoding conditional logic (`if user.isPremium show X else show Y`) throughout your widget tree
2. Waiting for a release cycle every time you want to change a banner, offer, or onboarding message

Intyx adds a **decision layer** between your backend and your UI. Your app sends a signal bundle (user segment, session count, active campaigns, etc.). The decision layer evaluates those signals, picks the right template from your widget catalog, fills in the parameters, and returns a ready-to-render widget response. Your Flutter component renders it — no conditional logic needed in the app.

---

## How it works

```
Flutter App  →  signal bundle  →  Decision Layer  →  Template Catalog
                                        ↓
                             Widget Response (type + params)
                                        ↓
                             DynamicWidgetContainer renders it
```

**Three layers:**

1. **Predefined templates** — a catalog of typed widget layouts (hero, promo, countdown, progress, poll, etc.)
2. **Live signal inputs** — user data, external APIs (weather, news, trends), seasonal events, developer-defined params
3. **Decision layer** — evaluates signals against your catalog, selects the best match, fills parameters

---

## Use cases

- **Onboarding variants** — show different welcome flows based on signup source
- **Campaign banners** — push seasonal or event-based cards without a release
- **Paywall experiments** — test different upsell messages across user segments
- **Dashboard cards** — surface contextual tips, alerts, or stats per user context

---

## Quick start

### 1. Backend

```bash
cd server
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add at minimum: GEMINI_API_KEY and INTYX_DEV_MODE=true (dev only)

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

### 3. Flutter — add the package

```yaml
# pubspec.yaml
dependencies:
  intyx_dynamic_widget:
    path: ../flutter_client
```

### 4. Flutter — initialise and use

```dart
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();  // registers all built-in templates
  runApp(MyApp());
}
```

```dart
// In your screen or widget tree
DynamicWidgetContainer(
  responseJson: widgetResponse,          // JSON from your /api/widgets/evaluate call
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onAction: (widgetId, action) => handleAction(action),
)
```

### 5. Evaluate a widget for a user

```dart
final response = await http.post(
  Uri.parse('$apiUrl/api/widgets/evaluate'),
  headers: {'Authorization': 'Bearer $licenseKey'},
  body: jsonEncode({
    'user_id': userId,
    'session_count': sessionCount,
    'user_segment': 'premium',
    'custom_params': {'last_purchase_days_ago': 7},
  }),
);

final widgetResponse = jsonDecode(response.body);
// Pass widgetResponse to DynamicWidgetContainer
```

If the decision layer finds no matching widget, it returns `null` — `DynamicWidgetContainer` renders nothing. No crash.

---

## Key behaviour

| Property | Behaviour |
|---|---|
| **Fallback** | Returns `null` if no widget matches. Component renders nothing. Pass a custom `fallback` widget if needed. |
| **Determinism** | Same signal bundle → same widget, every time. Selection is rule-based, not probabilistic. |
| **Guardrails** | Only predefined template types can be rendered. The backend cannot inject arbitrary Flutter code. |
| **Dev mode** | Set `INTYX_DEV_MODE=true` in backend `.env` to bypass license checks during development. Never use in production. |

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.x, Gunicorn |
| Database | Firebase Firestore |
| Decision layer | Google Gemini (gemini-2.0-flash) — used as orchestration engine, not for UI generation |
| Flutter SDK | Dart, Flutter — drop-in `DynamicWidgetContainer` component |
| Web Dashboard | React 18, Vite 5, React Router 6 |
| Payments | Paddle (webhook + client-side checkout) |
| MCP | Model Context Protocol server (for Cursor/Claude Desktop integration) |
| Tests | pytest (61 backend tests), Flutter test |
| Deploy | Docker, Cloud Run, Vercel/Netlify |

---

## Project structure

```
intyx-dynamic-widget/
├── server/                   # Python backend (Flask, decision layer, data sources)
│   ├── app.py
│   ├── ai/                   # Gemini client
│   ├── routes/               # REST API endpoints
│   ├── data_sources/         # Weather, news, trends, horoscope
│   ├── triggers/             # Signal evaluation engine
│   ├── mcp/                  # MCP server for IDE integration
│   └── tests/                # 61 backend tests
├── flutter_client/           # Flutter SDK package
│   └── lib/
│       ├── core/             # Widget registry, resolver, SDK init
│       ├── models/           # WidgetDefinition, response models
│       ├── services/         # Backend API + Firestore listener
│       └── widgets/          # 15+ built-in widget templates
├── web/                      # React dashboard (Widget Studio, Agent Tasks, Pricing)
├── example/                  # Flutter example app
└── docs/                     # Architecture, deploy guides, API keys reference
```

---

## Running tests

```bash
cd /path/to/intyx-dynamic-widget
python -m pytest server/tests/ -v
# 61 tests: models, triggers, API endpoints, data sources
```

---

## Environment variables

**Required (backend):**

```env
GEMINI_API_KEY=<from aistudio.google.com>
FIREBASE_PROJECT_ID=<your-firebase-project>
INTYX_DEV_MODE=true          # dev only — disables license checks
```

**Optional (backend):**

```env
INTYX_SERVER_API_KEY=<generate with: openssl rand -hex 32>
FIREBASE_CREDENTIALS_PATH=/app/serviceAccountKey.json
```

**Frontend (web/.env):**

```env
VITE_API_URL=http://localhost:8080   # or your deployed backend URL
```

See [`docs/API-KEYS.md`](docs/API-KEYS.md) for the full reference.

---

## Docs

| Document | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Detailed architecture and data flow |
| [docs/API-KEYS.md](docs/API-KEYS.md) | All API keys and environment variables |
| [docs/DEPLOY-SERVER.md](docs/DEPLOY-SERVER.md) | Backend deploy (Cloud Run, Railway, Docker) |
| [docs/DEPLOY-WEB.md](docs/DEPLOY-WEB.md) | Web deploy (Vercel, Netlify) |
| [docs/FIREBASE-SETUP.md](docs/FIREBASE-SETUP.md) | Firebase Firestore setup |
| [docs/MCP-SERVER.md](docs/MCP-SERVER.md) | MCP server setup for Cursor/Claude Desktop |

---

## License

MIT — see LICENSE file.

> This is an experimental project. Use it, break it, improve it, share feedback.
