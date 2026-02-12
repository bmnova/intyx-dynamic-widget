# API Key’ler ve Ortam Değişkenleri

Projede kullanılan tüm API key’ler ve nereden alınacakları. Değerleri **asla** repoya commit etmeyin; `.env` veya platform Environment Variables ile verin.

---

## Zorunlu (server çalışması için)

| Değişken | Açıklama | Nereden alınır |
|----------|----------|----------------|
| `FIREBASE_PROJECT_ID` | Firebase proje ID | [Firebase Console](https://console.firebase.google.com) → Proje ayarları → Proje ID. Varsayılan: `intyx-dynamic-widget` (proje adınız farklıysa değiştirin). |
| `GEMINI_API_KEY` | AI widget önerileri ve agent görevleri | [Google AI Studio](https://aistudio.google.com/apikey) → Create API key. |

---

## Önerilen (production için)

| Değişken | Açıklama | Nereden alınır |
|----------|----------|----------------|
| `FIREBASE_CREDENTIALS_PATH` | Service account JSON dosya yolu | Firebase Console → Proje ayarları → Service accounts → “Generate new private key”. İndirilen JSON’ı güvenli bir yere koyun, yolunu bu değişkene yazın. **Cloud Run / GCP’de çalışırken boş bırakılabilir** (Application Default Credentials kullanılır). |

### TODO — Test sonrası eklenecek

| Değişken | Açıklama |
|----------|----------|
| `INTYX_SERVER_API_KEY` | Backend API koruma anahtarı. Şimdilik atlanıyor; test ettikten sonra ekleyin. Kendiniz üretin (uzun rastgele string). Dashboard / widget / AI endpoint’lerine isteklerde `Authorization: Bearer <bu_key>` veya body/query’de `api_key` gönderilir. Boş bırakırsanız tüm endpoint’ler korumasız kalır. |

---

## Opsiyonel (özellik bazlı)

| Değişken | Açıklama | Nereden alınır |
|----------|----------|----------------|
| `OPENWEATHER_API_KEY` | Hava durumu verisi | [OpenWeather](https://openweathermap.org/api) → Sign in → API keys. Yoksa hava widget’ları placeholder veri kullanır. |
| `TWITTER_BEARER_TOKEN` | Trend verisi (Twitter/X) | [Twitter Developer](https://developer.twitter.com) → App → Keys and tokens → Bearer Token. Yoksa trend verisi kullanılmaz. |
| `TRENDS_REGION` | Trend bölgesi | ISO ülke kodu (örn. `TR`, `US`). Varsayılan: `TR`. |

---

## Web (frontend) – Vite

Bunlar **build zamanında** `import.meta.env` ile enjekte edilir. Deploy platformunda (Vercel, Netlify vb.) Environment Variables olarak ekleyin.

| Değişken | Açıklama | Nereden alınır |
|----------|----------|----------------|
| `VITE_API_URL` | Backend API base URL | Deploy ettiğiniz server URL’i (örn. `https://api.intyx.dev` veya Cloud Run URL). Yerel: `http://localhost:8080`. |
| `VITE_PADDLE_ENV` | Paddle ortamı | `sandbox` veya `production`. |
| `VITE_PADDLE_PUBLISHABLE_TOKEN` | Paddle publishable key | Paddle Dashboard → Developer tools → Authentication. |
| `VITE_PADDLE_PRICE_IDS` | Paddle plan → price id | JSON string: `{"pro":"pri_xxx","enterprise":"pri_yyy"}`. Paddle Catalog’da oluşturduğunuz price id’ler. |

---

## Hızlı aktivasyon (yerel)

1. **Server:** `server/.env` oluşturun (veya repo kökünde `server/` için `cp server/.env.example server/.env`). İçine en azından şunları yazın:
   ```bash
   FIREBASE_PROJECT_ID=intyx-dynamic-widget
   GEMINI_API_KEY=your-gemini-api-key
   # TODO: Test sonrası INTYX_SERVER_API_KEY ekleyin
   # İsteğe bağlı:
   # FIREBASE_CREDENTIALS_PATH=./path/to/serviceAccountKey.json
   # OPENWEATHER_API_KEY=...
   ```
2. **Web:** `web/.env` oluşturun:
   ```bash
   VITE_API_URL=http://localhost:8080
   # Paddle (opsiyonel):
   # VITE_PADDLE_ENV=sandbox
   # VITE_PADDLE_PUBLISHABLE_TOKEN=test_xxx
   # VITE_PADDLE_PRICE_IDS={"pro":"pri_xxx","enterprise":"pri_yyy"}
   ```
3. Server’ı `.env` ile çalıştırın (aşağıda dotenv ekliyoruz — `python server/app.py` veya `flask run` ile `.env` otomatik yüklenecek).

`.env` dosyaları `.gitignore`’da olduğu için repoya gitmez.

---

## Cloud deploy

- **Backend (server):** [DEPLOY-SERVER.md](./DEPLOY-SERVER.md) — Cloud Run, Railway, Render, Docker.
- **Web (frontend):** [DEPLOY-WEB.md](./DEPLOY-WEB.md) — Vercel, Netlify, env değişkenleri.
