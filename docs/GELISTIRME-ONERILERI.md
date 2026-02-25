# Geliştirme Önerileri

Bu doküman, Intyx Dynamic Widget sisteminin mevcut durumunu analiz ederek belirlenen geliştirme alanlarını öncelik sırasıyla listeler.

---

## Mevcut Durum Özeti

| Alan | Durum |
|------|-------|
| Backend (Python/Flask) | Üretim hazır, 61 test |
| Flutter SDK | Üretim hazır, 16 widget tipi |
| Web Dashboard (React) | Çalışıyor, TypeScript yok |
| MCP Server | 24 tool, Gemini entegrasyonu |
| CI/CD | GitHub Actions pipeline mevcut |
| Test (web) | **Yok** |
| Monitoring | **Yok** |

---

## Yüksek Öncelik

### 1. Web Testleri Ekle

**Neden:** Web frontend için sıfır test var. Kod değişikliklerinde regresyon riski yüksek.

**Yapılacaklar:**
- Vitest + React Testing Library kurulumu
- `WidgetStudio.jsx`, `AgentTasks.jsx`, `Dashboard.jsx` için birim testler
- Temel sayfa render testleri (`Landing`, `Pricing`)
- API çağrıları için mock kurulumu

**Tahmini kapsam:** En az 20–30 test

---

### 2. TypeScript Geçişi (Web)

**Neden:** Web frontend tamamen `.jsx`. Tip hatalarını geliştirme aşamasında yakalamak için TypeScript şart.

**Yapılacaklar:**
- `tsconfig.json` ekle, `vite.config.js` güncelle
- `.jsx` → `.tsx` dönüşümü (sayfa + bileşenler)
- API yanıt tipleri için ortak `types/` klasörü
- Paddle ve config dosyaları için tip tanımları

**Tavsiye:** Bileşenleri tek tek taşı, birden geçmeye çalışma.

---

### 3. Analytics Dashboard

**Neden:** Widget görüntüleme, tıklama ve dismiss verisi toplanıyor (Firestore'da `user_states`) ama görselleştirilmiyor.

**Yapılacaklar:**
- Web dashboard'a yeni "Analytics" sayfası ekle
- Widget başına gösterim / tıklama / dismiss sayısı
- En çok / en az etkileşim alan widget'lar
- Zaman bazlı grafik (günlük / haftalık)
- Recharts veya Chart.js ile görselleştirme

---

## Orta Öncelik

### 4. Redis / Valkey Cache

**Neden:** Şu an Firestore cache-first pattern kullanılıyor. Yük altında Firestore okuma maliyeti ve gecikme artıyor.

**Yapılacaklar:**
- `redis-py` bağımlılığı ekle
- Hava durumu, haberler, burç, trend verilerini Redis'te cache'le (TTL: 15–60 dk)
- Firestore'u Redis miss durumunda fallback olarak kullan
- `REDIS_URL` env değişkeni ekle (Railway / Upstash ücretsiz tier)

---

### 5. JWT Tabanlı Kimlik Doğrulama

**Neden:** Mevcut sistem API key + License key ikili sistemi kullanıyor. JWT ile kullanıcı bazlı oturumlar ve daha ince izin kontrolü mümkün.

**Yapılacaklar:**
- `PyJWT` bağımlılığı ekle
- `/api/auth/login` ve `/api/auth/refresh` endpoint'leri
- Kısa ömürlü access token (15 dk) + uzun ömürlü refresh token
- Mevcut API key sistemini kaldırma (geriye dönük uyumluluk için aşamalı)

---

### 6. A/B Testing Framework

**Neden:** Hangi widget'ın hangi kullanıcı grubunda daha iyi performans gösterdiği bilinmiyor.

**Yapılacaklar:**
- `experiments` Firestore koleksiyonu ekle
- Widget'lara `experiment_id` ve `variant` alanı ekle
- `/api/experiments` endpoint'leri (oluştur, sonuç gör)
- Flutter SDK'ya deney katılım ve sonuç gönderme

---

### 7. Kullanıcı Segmentasyonu

**Neden:** Tüm kullanıcılar aynı widget'ları görüyor. Segmente özel widget'lar çok daha yüksek dönüşüm sağlar.

**Yapılacaklar:**
- Widget tanımına `target_segments` alanı ekle
- Segment kriterleri: platform, dil, uygulama versiyonu, özel etiketler
- Flutter SDK'ya segment metadata gönderme
- Trigger engine'e segment filtresi ekle

---

### 8. Widget Zamanlama

**Neden:** Belirli saatlerde veya tarih aralıklarında gösterilmesi gereken widget'lar mevcut trigger sistemiyle yönetilemez.

**Yapılacaklar:**
- Widget'a `show_from`, `show_until`, `show_hours` (örn. 08:00–20:00) alanları ekle
- Trigger engine'e zaman bazlı condition ekle
- Web dashboard'da takvim görünümü ile zamanlama

---

### 9. Streaming AI Yanıtı

**Neden:** Gemini içerik üretimi uzun sürebiliyor; kullanıcı sonucu bekliyor.

**Yapılacaklar:**
- `/api/ai/generate-content` endpoint'ine SSE (Server-Sent Events) desteği ekle
- Web dashboard'da stream'i anlık göster
- Flutter SDK'da stream yanıtını işle

---

## Düşük Öncelik

### 10. React Native SDK

**Neden:** Flutter SDK mevcut ama React Native pazarı da büyük.

**Yapılacaklar:**
- `react-native-intyx-widget` paketi oluştur
- Aynı REST API'yi kullanan JSON-driven rendering
- npm'e yayınla

---

### 11. Kubernetes Manifests

**Neden:** Şu an sadece Dockerfile ve Railway/Render config var. Kurumsal müşteriler k8s ister.

**Yapılacaklar:**
- `k8s/` klasörü oluştur
- Deployment, Service, Ingress, ConfigMap, Secret manifest'leri
- Horizontal Pod Autoscaler (HPA) config
- Helm chart (opsiyonel)

---

### 12. Monitoring & Observability

**Neden:** Production'da neler olduğu görülmüyor (Sentry opsiyonel olarak eklenmiş ama yeterli değil).

**Yapılacaklar:**
- Prometheus metrics endpoint (`/metrics`) ekle: request sayısı, latency, hata oranı
- Grafana dashboard şablonu hazırla
- Structured logging (JSON format, log level)
- Uptime monitoring (Better Uptime / UptimeRobot)

---

### 13. Kullanım Raporu E-postası

**Neden:** Müşteriler aylık ne kadar widget görüntülendiğini görmek ister.

**Yapılacaklar:**
- Aylık kullanım özeti e-postası (Resend / SendGrid)
- `/api/usage/report` endpoint'i
- Lisans planı kullanım yüzdesi gösterimi

---

### 14. API Versiyonlama

**Neden:** API değişikliklerinde mevcut istemciler bozulabilir. Versiyon stratejisi yok.

**Yapılacaklar:**
- URL prefix: `/api/v1/` → `/api/v2/`
- Deprecation header'ları
- Sürüm geçiş rehberi dokümanı

---

### 15. Dark Mode (Web Dashboard)

**Neden:** Web dashboard'da dark mode yok. Geliştirici hedef kitlesi dark mode bekler.

**Yapılacaklar:**
- Tailwind `dark:` class'ları veya CSS değişkenleri
- Sistem tercihini otomatik algıla (`prefers-color-scheme`)
- Manuel toggle (Navbar'da)

---

### 16. i18n / Çoklu Dil Desteği

**Neden:** Proje Türkçe dokümanlı ama widget içerikleri İngilizce. Global pazara açılmak için i18n şart.

**Yapılacaklar:**
- `react-i18next` ile web dashboard çevirisi
- Widget içeriklerinde `locale` parametresi
- Flutter SDK'da `locale` ile içerik getirme
- TR ve EN başlangıç çevirileri

---

## Öncelik Özeti

| # | Geliştirme | Öncelik | Etki | Zorluk |
|---|---|---|---|---|
| 1 | Web testleri ekle | Yüksek | Kod güvenilirliği | Düşük |
| 2 | TypeScript geçişi | Yüksek | Bakım kolaylığı | Orta |
| 3 | Analytics dashboard | Yüksek | Kullanıcı değeri | Orta |
| 4 | Redis cache | Orta | Performans | Düşük |
| 5 | JWT auth | Orta | Güvenlik | Orta |
| 6 | A/B testing | Orta | İş değeri | Yüksek |
| 7 | Kullanıcı segmentasyonu | Orta | İş değeri | Orta |
| 8 | Widget zamanlama | Orta | Özellik | Düşük |
| 9 | Streaming AI | Orta | UX | Orta |
| 10 | React Native SDK | Düşük | Pazar | Yüksek |
| 11 | Kubernetes | Düşük | Altyapı | Yüksek |
| 12 | Monitoring | Düşük | Operasyon | Orta |
| 13 | Kullanım raporu | Düşük | Müşteri değeri | Düşük |
| 14 | API versiyonlama | Düşük | Bakım | Düşük |
| 15 | Dark mode | Düşük | UX | Düşük |
| 16 | i18n | Düşük | Global pazar | Orta |
