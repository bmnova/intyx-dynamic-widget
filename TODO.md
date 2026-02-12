# TODO

## Server

### Guvenlik
- [x] Tum endpoint'lere API key validation middleware ekle (su an hepsi public)
- [x] Rate limiting ekle (Flask-Limiter vb.)
- [x] API key'leri request body yerine Authorization header'da tasi
- [x] Widget create endpoint'ine input validation ekle (type, params schema kontrolu)
- [x] Weather input'unda type checking ekle (temperature/humidity string gelebilir)

### Stabilite
- [x] Firebase init'i thread-safe yap (threading.Lock ile double-check locking)
- [x] Scheduler'a exponential backoff ekle (API hatalari icin)
- [x] Weather source'a connection/timeout exception handling ekle
- [x] Gemini JSON parsing'de edge case duzelt (markdown fence'siz "```" gelirse IndexError)
- [x] Eksik environment variable'lar icin startup validation ekle (fail fast)

### Veri Butunlugu
- [x] Firestore array update'lerinde transaction kullan (race condition onleme)
- [x] record_interaction ve record_user_action action type'larini ayir (ayni array'de karisiyor)

### Performans
- [x] Widget ve trigger rule sorgularina pagination ekle
- [x] Firestore index'leri olustur

### Kod Kalitesi
- [x] `_build_conditions` fonksiyonunu routes.widgets'tan shared utility'ye tasi (MCP'den import ediliyor)
- [x] Gemini model adini config.py'a tasi (su an hardcoded "gemini-2.0-flash")

## Web (React)

### Guvenlik & UX
- [x] Pricing.jsx'te alert() yerine duzgun UI notification kullan
- [x] 404 route ekle (bilinmeyen path'lerde bos sayfa gorunuyor)
- [x] Protected route wrapper ekle (Dashboard/AgentTasks icin route seviyesinde guard)

### Genel
- [x] SEO meta tag'leri ekle (description, Open Graph, Twitter card)
- [ ] Accessibility iyilestir (aria-label, keyboard navigation)

## Flutter

### Genel
- [x] DynamicWidgetContainer'daki redundant Theme wrapping'i kaldir (ResponsiveWidgetWrapper zaten yapiyor)
- [x] License validation'a strict mode ekle (production'da offline fallback'i kapatan flag)
- [x] EdgeInsets parsing sirasini dokumante et (CSS standardindan farkli)

## Altyapi

### Production Oncesi
- [ ] Test sonrası `INTYX_SERVER_API_KEY` ekle (şimdilik endpoint'ler korumasız)
- [ ] Paddle odeme entegrasyonunu tamamla
- [x] CI/CD pipeline kur
- [x] Logging ve monitoring ekle
- [x] Firestore security rules yaz
