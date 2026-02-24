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
