# intyx_dynamic_widget

Dynamic widget system for Flutter apps. AI-driven, JSON-configured, responsive widgets with 15+ built-in UI components.

## Features

- **JSON-driven rendering** – Widgets are defined by JSON and rendered via `DynamicWidgetContainer`
- **15+ built-in UI types** – Banner, Carousel, Hero Image, Countdown, Poll, Rating, Profile, Progress, Social Proof, and more
- **Widget categories** – Promotional, Informational, Contextual, Functional
- **Responsive layout** – `ResponsiveWidgetWrapper` for adaptive sizing
- **Catalog system** – `CatalogProvider` and `WidgetRegistry` for widget discovery
- **Firebase** – Optional integration via `FirebaseService`
- **Priority & dismiss** – Priority-based ordering and dismissible widgets
- **Actions** – `onAction` and `onDismiss` callbacks

## Installation

Add to your `pubspec.yaml`:

```yaml
dependencies:
  intyx_dynamic_widget: ^0.1.0
```

Then run:

```bash
flutter pub get
```

## Usage

### 1. Register built-in widgets (once at startup)

```dart
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();
  runApp(MyApp());
}
```

### 2. Initialize (e.g. with Firebase)

```dart
await IntyxInit.initialize(
  firebaseProjectId: 'your-project-id',
  // optional: catalogJsonUrl, widgetServiceBaseUrl
);
```

### 3. Show dynamic widgets

```dart
DynamicWidgetContainer(
  triggerContext: TriggerContext(
    userId: 'user-123',
    locale: 'en',
    platform: 'mobile',
  ),
  onAction: (actionId, payload) => {},
  onDismiss: (widgetId) => {},
)
```

### 4. Use a single widget from JSON

```dart
final widget = WidgetDefinition.fromJson(jsonMap);
// Use with your registered builders via WidgetResolver or render directly
```

## Topics

- widget
- dynamic-ui
- json
- ai

## License

MIT – see [LICENSE](LICENSE) for details.
