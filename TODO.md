# TODO

## Server

### Guvenlik
- [ ] Tum endpoint'lere API key validation middleware ekle (su an hepsi public)
- [ ] Rate limiting ekle (Flask-Limiter vb.)
- [ ] API key'leri request body yerine Authorization header'da tasi
- [ ] Widget create endpoint'ine input validation ekle (type, params schema kontrolu)
- [ ] Weather input'unda type checking ekle (temperature/humidity string gelebilir)

### Stabilite
- [ ] Firebase init'i thread-safe yap (threading.Lock ile double-check locking)
- [ ] Scheduler'a exponential backoff ekle (API hatalari icin)
- [ ] Weather source'a connection/timeout exception handling ekle
- [ ] Gemini JSON parsing'de edge case duzelt (markdown fence'siz "```" gelirse IndexError)
- [ ] Eksik environment variable'lar icin startup validation ekle (fail fast)

### Veri Butunlugu
- [ ] Firestore array update'lerinde transaction kullan (race condition onleme)
- [ ] record_interaction ve record_user_action action type'larini ayir (ayni array'de karisiyor)

### Performans
- [ ] Widget ve trigger rule sorgularina pagination ekle
- [ ] Firestore index'leri olustur

### Kod Kalitesi
- [ ] `_build_conditions` fonksiyonunu routes.widgets'tan shared utility'ye tasi (MCP'den import ediliyor)
- [ ] Gemini model adini config.py'a tasi (su an hardcoded "gemini-2.0-flash")

## Web (React)

### Guvenlik & UX
- [ ] Pricing.jsx'te alert() yerine duzgun UI notification kullan
- [ ] 404 route ekle (bilinmeyen path'lerde bos sayfa gorunuyor)
- [ ] Protected route wrapper ekle (Dashboard/AgentTasks icin route seviyesinde guard)

### Genel
- [ ] SEO meta tag'leri ekle (description, Open Graph, Twitter card)
- [ ] Accessibility iyilestir (aria-label, keyboard navigation)

## Flutter

### Genel
- [ ] DynamicWidgetContainer'daki redundant Theme wrapping'i kaldir (ResponsiveWidgetWrapper zaten yapiyor)
- [ ] License validation'a strict mode ekle (production'da offline fallback'i kapatan flag)
- [ ] EdgeInsets parsing sirasini dokumante et (CSS standardindan farkli)

## Altyapi

### Production Oncesi
- [ ] Paddle odeme entegrasyonunu tamamla
- [ ] CI/CD pipeline kur
- [ ] Logging ve monitoring ekle
- [ ] Firestore security rules yaz
