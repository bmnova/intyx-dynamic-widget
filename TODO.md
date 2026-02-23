# TODO

## Tamamlananlar

### Server — Guvenlik
- [x] Tum endpoint'lere API key validation middleware ekle
- [x] Rate limiting ekle (Flask-Limiter)
- [x] API key'leri Authorization header'da tasi
- [x] Widget create endpoint'ine input validation ekle
- [x] Weather input'unda type checking ekle

### Server — Stabilite
- [x] Firebase init'i thread-safe yap (double-check locking)
- [x] Scheduler'a exponential backoff ekle
- [x] Weather source'a connection/timeout exception handling ekle
- [x] Gemini JSON parsing'de edge case duzelt
- [x] Eksik environment variable'lar icin startup validation ekle (fail fast)

### Server — Veri Butunlugu
- [x] Firestore array update'lerinde transaction kullan
- [x] record_interaction ve record_user_action action type'larini ayir

### Server — Performans
- [x] Widget ve trigger rule sorgularina pagination ekle
- [x] Firestore index'leri olustur

### Server — Kod Kalitesi
- [x] `_build_conditions` fonksiyonunu shared utility'ye tasi
- [x] Gemini model adini config.py'a tasi

### Server — Yeni Ozellikler
- [x] Auth middleware (server key + license key dual-level)
- [x] Paddle webhook handler (HMAC-SHA256 dogrulama)
- [x] Otomatik lisans olusturma (Paddle transaction.completed)
- [x] Lisans iptal (Paddle subscription.canceled)
- [x] Plan limit enforcement (widget create'te kontrol)
- [x] Sentry error tracking (opsiyonel)
- [x] NewsAPI.org gercek entegrasyonu
- [x] Gemini AI ile burc yorumu (batch 12 burc)
- [x] MCP handler registry pattern (monolith'ten modular'e)
- [x] Tool definitions single source of truth
- [x] Gemini agent auto-generated declarations
- [x] Lisans ve agent task Firestore persistence

### Web (React)
- [x] Pricing.jsx'te alert() yerine Toast notification
- [x] 404 route ekle
- [x] Protected route wrapper ekle
- [x] SEO meta tag'leri ekle
- [x] Widget Studio sayfasi (3-adim: sec, prompt, onizle)
- [x] Dashboard quick action cards

### Flutter
- [x] DynamicWidgetContainer redundant Theme wrapping kaldir
- [x] License validation'a strict mode ekle
- [x] EdgeInsets parsing sirasini dokumante et

### Altyapi
- [x] CI/CD pipeline kur
- [x] Logging ve monitoring ekle
- [x] Firestore security rules yaz
- [x] Firestore indexes deploy

---

## Yapilacaklar

### Kritik (Production Oncesi)
- [ ] `INTYX_SERVER_API_KEY` production'da aktif et (test sonrasi)
- [ ] Flutter SDK'da lisans dogrulama (widget renderer'da server-side kontrol)

### Onemli
- [ ] SDK analytics — widget impression/interaction event tracking
- [ ] Flutter offline caching — son widget state'i local'de tut
- [ ] OpenAPI/Swagger API dokumantasyonu
- [ ] Web accessibility iyilestir (aria-label, keyboard navigation)

### Guzel Olur
- [ ] Landing page'de interaktif widget demo
- [ ] Widget A/B testing mekanizmasi
- [ ] Multi-language widget content support
- [ ] Admin dashboard (lisans yonetimi, kullanim analytics)
- [ ] Flutter SDK pub.dev'e yayinla
