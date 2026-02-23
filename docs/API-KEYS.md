# API Key'ler ve Ortam Degiskenleri

Projede kullanilan tum API key'ler ve nereden alinacaklari. Degerleri **asla** repoya commit etmeyin; `.env` veya platform Environment Variables ile verin.

---

## Zorunlu (server calismasi icin)

| Degisken | Aciklama | Nereden alinir |
|----------|----------|----------------|
| `FIREBASE_PROJECT_ID` | Firebase proje ID | [Firebase Console](https://console.firebase.google.com) → Proje ayarlari → Proje ID. Varsayilan: `intyx-dynamic-widget`. |
| `GEMINI_API_KEY` | AI widget onerileri ve agent gorevleri | [Google AI Studio](https://aistudio.google.com/apikey) → Create API key. |

---

## Onerilen (production icin)

| Degisken | Aciklama | Nereden alinir |
|----------|----------|----------------|
| `INTYX_SERVER_API_KEY` | Backend API koruma anahtari | Kendiniz uretin (uzun rastgele string, orn. `openssl rand -hex 32`). Bos birakirsaniz tum endpoint'ler korumasiz kalir. Isteklerde `Authorization: Bearer <key>` header'i ile gonderilir. |
| `FIREBASE_CREDENTIALS_PATH` | Service account JSON dosya yolu | Firebase Console → Proje ayarlari → Service accounts → "Generate new private key". Cloud Run / GCP'de bos birakin (Application Default Credentials kullanilir). |

---

## Opsiyonel (ozellik bazli)

| Degisken | Aciklama | Nereden alinir | Varsayilan |
|----------|----------|----------------|------------|
| `OPENWEATHER_API_KEY` | Hava durumu verisi | [OpenWeather](https://openweathermap.org/api) → Sign in → API keys | Bos (placeholder veri) |
| `TWITTER_BEARER_TOKEN` | Trend verisi (Twitter/X) | [Twitter Developer](https://developer.twitter.com) → App → Keys → Bearer Token | Bos (trend verisi yok) |
| `TRENDS_REGION` | Trend bolgesi (ISO ulke kodu) | — | `TR` |
| `NEWS_API_KEY` | Haber verisi | [NewsAPI.org](https://newsapi.org) → Get API Key | Bos (bos haber listesi) |
| `NEWS_API_COUNTRY` | Haber ulkesi (ISO ulke kodu) | — | `tr` |
| `PADDLE_WEBHOOK_SECRET` | Paddle webhook imza dogrulama | Paddle Dashboard → Developer tools → Webhooks → Secret key | Bos (webhook dogrulama devre disi) |
| `SENTRY_DSN` | Hata takip | [Sentry](https://sentry.io) → Project → Settings → Client Keys (DSN) | Bos (Sentry devre disi) |
| `GEMINI_MODEL_NAME` | Kullanilacak Gemini modeli | — | `gemini-2.0-flash` |

---

## Server Konfigurasyonu (opsiyonel)

| Degisken | Aciklama | Varsayilan |
|----------|----------|------------|
| `HOST` | Sunucu bind adresi | `0.0.0.0` |
| `PORT` | Sunucu portu | `8080` |
| `RATE_LIMIT_DEFAULT` | Genel rate limit | `200 per hour` |
| `RATE_LIMIT_AI` | AI endpoint rate limit | `30 per minute` |
| `WEATHER_POLL_INTERVAL` | Hava durumu polling suresi (saniye) | `300` (5 dk) |
| `NEWS_POLL_INTERVAL` | Haber polling suresi (saniye) | `600` (10 dk) |
| `HOROSCOPE_POLL_INTERVAL` | Burc polling suresi (saniye) | `3600` (1 saat) |
| `TRENDS_POLL_INTERVAL` | Trend polling suresi (saniye) | `900` (15 dk) |

---

## Web (frontend) — Vite

Build zamaninda `import.meta.env` ile enjekte edilir. Deploy platformunda Environment Variables olarak ekleyin.

| Degisken | Aciklama | Nereden alinir |
|----------|----------|----------------|
| `VITE_API_URL` | Backend API base URL | Deploy ettiginiz server URL (orn. `https://api.intyx.dev`). Yerel: `http://localhost:8080`. |
| `VITE_PADDLE_ENV` | Paddle ortami | `sandbox` veya `production` |
| `VITE_PADDLE_PUBLISHABLE_TOKEN` | Paddle publishable key | Paddle Dashboard → Developer tools → Authentication |
| `VITE_PADDLE_PRICE_IDS` | Plan → price id esleme (JSON) | `{"pro":"pri_xxx","enterprise":"pri_yyy"}` — Paddle Catalog'da olusturdunuz price id'ler |

---

## Hizli Aktivasyon (yerel)

### 1. Server

```bash
cp server/.env.example server/.env
# Dosyayi acip asagidaki zorunlu key'leri doldurun:
```

```bash
# server/.env
FIREBASE_PROJECT_ID=intyx-dynamic-widget
GEMINI_API_KEY=your-gemini-api-key

# Onerilen (production icin):
# INTYX_SERVER_API_KEY=your-random-secret-key
# FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json

# Opsiyonel:
# OPENWEATHER_API_KEY=your-openweather-key
# NEWS_API_KEY=your-newsapi-key
# TWITTER_BEARER_TOKEN=your-twitter-token
# PADDLE_WEBHOOK_SECRET=your-paddle-secret
# SENTRY_DSN=your-sentry-dsn
```

### 2. Web

```bash
cp web/.env.example web/.env
```

```bash
# web/.env
VITE_API_URL=http://localhost:8080

# Paddle (opsiyonel):
# VITE_PADDLE_ENV=sandbox
# VITE_PADDLE_PUBLISHABLE_TOKEN=test_xxx
# VITE_PADDLE_PRICE_IDS={"pro":"pri_xxx","enterprise":"pri_yyy"}
```

### 3. Calistir

```bash
# Backend
cd server && python -m server.app

# Web (ayri terminal)
cd web && npm run dev
```

`.env` dosyalari `.gitignore`'da oldugu icin repoya gitmez.

---

## Cloud Deploy

- **Backend (server):** [DEPLOY-SERVER.md](./DEPLOY-SERVER.md) — Cloud Run, Railway, Render, Docker
- **Web (frontend):** [DEPLOY-WEB.md](./DEPLOY-WEB.md) — Vercel, Netlify, Firebase Hosting
