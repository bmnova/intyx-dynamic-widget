# Web Deploy Rehberi

Bu dokumanda **web/** (Vite + React) uygulamasini canliya alma adimlari anlatiliyor.

---

## Build (yerel test)

```bash
cd web
npm install   # ilk seferde; CI'da npm ci kullanin
npm run build
```

Cikti: **`web/dist/`**

**Yerel onizleme:**
- Gelistirme: `npm run dev` → **http://localhost:3000**
- Production: `npm run build && npm run preview` → **http://localhost:4173**

---

## 1. Vercel (onerilen)

### Yeni proje

1. [vercel.com](https://vercel.com) → GitHub ile giris
2. **Add New Project** → Repoyu sec
3. **Framework Preset:** Vite
4. **Root Directory:** `web`
5. **Deploy**

### Mevcut proje — Install Command hatasi

"cd web && npm ci" hatasi aliyorsaniz:

1. Vercel Dashboard → projeye gir → **Settings** → **Build & Development**
2. **Install Command** satirini bul → **Override** kapat veya alani bos birak
3. **Root Directory:** `web` secili olmali
4. **Save** → **Deployments** → **Redeploy**

---

## 2. Netlify

1. [netlify.com](https://netlify.com) → GitHub ile giris
2. **Add new site** → Repoyu sec
3. Build ayarlari:
   - **Base directory:** `web`
   - **Build command:** `npm run build`
   - **Publish directory:** `web/dist`
4. **Deploy site**

Alternatif: Proje kokunde `netlify.toml` zaten mevcut.

---

## 3. Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Public directory: web/dist
# Single-page app: Yes

cd web && npm run build && cd ..
firebase deploy --only hosting
```

---

## 4. GitHub Pages

1. Repo → **Settings** → **Pages** → Source: **GitHub Actions**
2. `vite.config.js` icinde base path gerekiyor:
   ```js
   base: process.env.GITHUB_PAGES === 'true' ? '/intyx-dynamic-widget/' : '/',
   ```

---

## Ortam Degiskenleri

| Degisken | Aciklama | Ornek |
|----------|----------|-------|
| `VITE_API_URL` | Backend API base URL | `https://api.intyx.dev` veya `http://localhost:8080` |
| `VITE_PADDLE_ENV` | Paddle ortami | `sandbox` veya `production` |
| `VITE_PADDLE_PUBLISHABLE_TOKEN` | Paddle publishable key | `test_xxx` veya `live_xxx` |
| `VITE_PADDLE_PRICE_IDS` | Plan → Price ID (JSON) | `{"pro":"pri_xxx","enterprise":"pri_yyy"}` |

Bu degerler build zamaninda `import.meta.env` ile enjekte edilir.

### Platform bazinda ayar

- **Vercel:** Project → Settings → Environment Variables
- **Netlify:** Site → Site settings → Environment variables
- **Firebase:** Build oncesi `.env.production` dosyasi olusturun

---

## Paddle Odeme Entegrasyonu

Web'de Pro/Enterprise odemeleri Paddle ile calisir.

### Kurulum

1. [Paddle](https://www.paddle.com) hesabi acin (sandbox + live)
2. Dashboard → **Catalog** → **Products** → urun ve **Price** olusturun
3. **Developer tools** → **Authentication** → publishable token kopyalayin
4. Env degiskenleri ayarlayin (yukardaki tablo)

### Webhook (backend tarafinda)

Paddle odeme tamamlaninca backend'e webhook gonderir:
- `POST /api/paddle/webhook` → HMAC-SHA256 dogrulama → otomatik lisans olusturma
- Backend'te `PADDLE_WEBHOOK_SECRET` env'i gerekli
- Paddle Dashboard → **Developer tools** → **Webhooks** → endpoint URL'nizi ekleyin

### Test

Pricing sayfasinda plan secip Paddle checkout'u acin. Sandbox'ta test kartlariyla odeme deneyin.

---

## Ozet

| Platform | Root dir | Build | Publish dir |
|----------|----------|-------|-------------|
| Vercel | `web` | `npm run build` | `dist` |
| Netlify | `web` | `npm run build` | `web/dist` |
| Firebase Hosting | — | `cd web && npm run build` | `web/dist` |
| GitHub Pages | `web` | `npm run build` (base: `/repo/`) | `dist` |

En hizli yol: GitHub repo baglayip **Vercel** veya **Netlify** ile import etmek.
