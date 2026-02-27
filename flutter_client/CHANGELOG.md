## 0.1.3

- **Documentation**: README now states that an API key from [dynamic.intyx.ai](https://dynamic.intyx.ai) is required; the package does not work without it.
- **Fixes**: Removed unnecessary casts in `WidgetEntry.fromJson`; removed redundant `dart:ui` import in tests. Analyzer clean with `dart analyze --fatal-infos`.

## 0.1.2

- **Full JSON response rendering**: All fields from widget JSON response (title, subtitle, body, cta, image, url, alias, text) are now displayed in widget previews.
- **Text & alias field support**: Widget types now properly render `text` and `alias` fields across all card types.
- **Improved JSON field mapping**: `DynamicWidgetContainer` and UI cards use complete field extraction from backend responses.

## 0.1.1

- **Offline cache**: Last widget response is cached locally via `shared_preferences`; shown on next launch while the network response is pending.
- **License validation**: SDK attaches `Authorization: Bearer <api_key>` to every backend request and validates the key on init.
- **Analytics**: Widget impressions and interaction events are automatically tracked via `WidgetService.recordImpression` / `recordInteraction`.
- **Strict mode**: `IntyxDynamicWidget.init()` now raises an `IntyxAuthException` when `strictMode: true` and the license key is invalid.
- Improved `DynamicWidgetContainer` — removed redundant `Theme` wrapping.
- `EdgeInsets` parsing order documented in `ResponsiveWidgetWrapper`.

## 0.1.0

- Initial release
- 15+ built-in UI widget types: Banner, Carousel, Hero Image, Countdown, Poll, Rating, Profile, Progress, Social Proof, and more
- JSON-driven dynamic widget rendering with `DynamicWidgetContainer`
- Widget categories: Promotional, Informational, Contextual, Functional
- Responsive layout support with `ResponsiveWidgetWrapper`
- Widget catalog system with `CatalogProvider` and `WidgetRegistry`
- Firebase integration via `FirebaseService`
- Priority-based widget ordering
- Dismissible widget support
- Action callback system (`onAction`, `onDismiss`)
- Dark mode compatible Material 3 design
