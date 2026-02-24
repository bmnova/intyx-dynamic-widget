# intyx_dynamic_widget

[![pub version](https://img.shields.io/pub/v/intyx_dynamic_widget)](https://pub.dev/packages/intyx_dynamic_widget)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**AI-driven, JSON-configured dynamic widget system for Flutter.**
An AI agent decides which widget to show and with which parameters — your app just renders the result.

---

## Features

| Feature | Details |
|---------|---------|
| **16 widget types** | Banner, Carousel, Hero Image, Countdown, Poll, Rating, Progress, Social Proof, Profile, Icon+Action, Clickable Image, Title+Subtitle, Promotional, Informational, Contextual, Functional |
| **JSON-driven** | `DynamicWidgetContainer` renders any widget from a JSON response |
| **Responsive layout** | Width, height, padding, margin, aspect ratio all configurable |
| **Dismissible** | Per-widget `dismissible` flag with `onDismiss` callback |
| **Action callbacks** | `onAction(widgetId, action)` for deep links, buttons, polls |
| **Priority ordering** | Widgets sorted by `priority` field automatically |
| **Offline cache** | Last widget response cached locally via `shared_preferences` |
| **License auth** | SDK attaches your API key to every backend request |

---

## Installation

```yaml
dependencies:
  intyx_dynamic_widget: ^0.1.1
```

```bash
flutter pub get
```

---

## Quick Start

### 1. Register built-in widget types (once at app start)

```dart
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();
  runApp(const MyApp());
}
```

### 2. Initialize the SDK

```dart
await IntyxDynamicWidget.init(
  apiKey: 'intyx_pro_xxxxxxxxxxxxxxxx',  // from intyx.dev/dashboard
);
```

### 3. Render widgets from an AI agent response

```dart
DynamicWidgetContainer(
  responseJson: agentResponse,           // Map<String, dynamic> from your backend
  colorScheme: Theme.of(context).colorScheme,
  padding: const EdgeInsets.all(12),
  onDismiss: (widgetId) => print('dismissed: $widgetId'),
  onAction: (widgetId, action) => handleAction(action),
)
```

### 4. Fetch widgets via the service

```dart
final service = WidgetService(baseUrl: 'https://your-backend.com');
final response = await service.resolveAgentTask(
  taskId: 'task_abc123',
  context: {
    'weather': 'sunny',
    'user_preferences': userPrefs,
    'current_date': DateTime.now().toIso8601String(),
  },
);
```

---

## Widget Types

### UI Cards
| Type | Class | Description |
|------|-------|-------------|
| `banner` | `BannerCard` | Simple text banner with optional emoji |
| `hero_image` | `HeroImageCard` | Full-width hero with overlay title and CTA |
| `carousel` | `CarouselCard` | Horizontal scrolling cards |
| `countdown_banner` | `CountdownBannerCard` | Live countdown timer |
| `clickable_image_link` | `ClickableImageLinkCard` | Tappable image with redirect |
| `title_subtitle_image` | `TitleSubtitleImageCard` | Card with title, subtitle, image |
| `icon_text_action` | `IconTextActionCard` | Icon + text + action button |
| `rating` | `RatingCard` | Star rating prompt |
| `poll` | `PollCard` | Single-choice voting |
| `social_proof` | `SocialProofCard` | Metric / testimonial |
| `progress` | `ProgressCard` | Progress bar with goal |
| `profile` | `ProfileCard` | User spotlight |

### Category Widgets
| Type | Class | Description |
|------|-------|-------------|
| `promotional` | `PromotionalWidget` | Campaign card with badge |
| `informational` | `InformationalWidget` | Notice / announcement |
| `contextual` | `ContextualWidget` | Context-aware (weather, horoscope …) |
| `functional` | `FunctionalWidget` | Action-focused, deep link support |

---

## Custom Widget Types

```dart
// Register a custom type alongside the built-ins
WidgetRegistry.register('my_custom_type', (params) {
  return MyCustomWidget(
    title: params['title'] as String,
    color: Color(int.parse(params['color'] as String)),
  );
});
```

---

## JSON Response Format

```json
{
  "widgets": [
    {
      "id": "w_abc123",
      "type": "banner",
      "params": {
        "emoji": "☀️",
        "text": "Good morning! Flash sale ends tonight."
      },
      "common": {
        "priority": 1,
        "dismissible": true,
        "ttl_seconds": 3600
      }
    }
  ]
}
```

---

## Backend

The SDK is designed to work with the [Intyx backend](https://github.com/bmnova/intyx-dynamic-widget/tree/master/server) — a Python/Flask API with Gemini AI integration. You can also bring your own backend as long as it returns the JSON format above.

Get an API key at [intyx.dev](https://intyx.dev).

---

## License

MIT — see [LICENSE](LICENSE) for details.
