# Intyx Dynamic Widget – Örnek Uygulama

Bu proje, **intyx_dynamic_widget** paketinin nasıl kullanılacağını gösteren örnek bir Flutter uygulamasıdır.

## Gereksinimler

- Flutter SDK (>=3.0.0)
- Proje kök dizininde `flutter_client` paketi (path: `../flutter_client`)

## Çalıştırma

Reponun kök dizininden:

```bash
cd example
flutter pub get
flutter run
```

Web için:

```bash
flutter run -d chrome
```

## Yapı

- **lib/main.dart** – Uygulama girişi, tema, `registerDefaultWidgets()` çağrısı.
- **lib/screens/home_screen.dart** – Ana sayfa; örnek ekranlara geçiş.
- **lib/screens/widget_feed_screen.dart** – Dinamik widget akışı: örnek agent JSON ile `DynamicWidgetContainer` kullanımı.

## Örnek Widget Tipleri

Örnekte kullanılan tipler: `contextual`, `promotional`, `hero_image`, `informational`, `icon_text_action`, `countdown_banner`, `functional`. Daha fazlası için ana paketin `widget_catalog.json` ve dokümantasyonuna bakın.

## Paket Bağlantısı

Örnek uygulama paketi yerel path ile kullanır:

```yaml
dependencies:
  intyx_dynamic_widget:
    path: ../flutter_client
```

Bu sayede `flutter_client` içinde yaptığınız değişiklikler örnek uygulamada anında yansır.
