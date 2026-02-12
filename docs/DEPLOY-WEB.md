# Web deploy rehberi

Bu dokümanda **web/** (Vite + React) uygulamasını canlıya alma adımları anlatılıyor.

## Build (yerel test)

```bash
cd web
npm install   # ilk seferde lock dosyası için; CI'da npm ci kullanın
npm run build
```

Not: `npm ci` kullanmak için önce bir kez `npm install` ile `package-lock.json` oluşturulmuş olmalı.

Çıktı: **`web/dist/`**

**Deploy öncesi PC’de görmek:**  
- Geliştirme: `npm run dev` → tarayıcıda **http://localhost:3000**  
- Production önizleme: `npm run build` sonra `npm run preview` → **http://localhost:4173**

---

## 1. Vercel (önerilen, GitHub ile)

### Yeni proje eklerken

1. [vercel.com](https://vercel.com) → GitHub ile giriş.
2. **Add New Project** → Repoyu seç (`intyx-dynamic-widget`).
3. **Framework Preset:** **Vite** seçin.
4. **Root Directory:** **Edit**’e tıklayıp **`web`** klasörünü seçin, **Continue**.
5. **Install Command** alanını **boş bırakın** (Override kapalı olsun).
6. **Build Command** ve **Output Directory** boş bırakın.
7. **Deploy** ile devam edin.

### "cd web && npm ci" hatası alıyorsan (mevcut proje)

Bu komut Vercel’in **kaydettiği proje ayarı**; repodaki dosyaları değiştirince otomatik düzelmez. Şunları yapın:

1. [vercel.com](https://vercel.com) → **Dashboard** → `intyx-dynamic-widget` projesine gir.
2. Üst menüden **Settings**’e tıkla.
3. Sol menüden **Build & Development**’ı aç.
4. **Build Command** bölümüne in.
5. **Install Command** satırını bul:
   - Yanında **Override** açıksa (veya `cd web && npm ci` yazıyorsa):
     - **Override**’ı kapat **veya** alanı tamamen sil (boş bırak).
   - Böylece Vercel, `web` kökünde `npm ci` kullanacak (`web/vercel.json`’dan).
6. **Root Directory** bölümüne bak: **`web`** seçili olmalı. Değilse **Edit** → `web` seç → Save.
7. **Save** (sayfa içinde varsa) yap.
8. **Deployments** sekmesine geç → en son deploy’un sağındaki **⋮** (üç nokta) → **Redeploy** → **Redeploy** onayla.

Yeni deploy’da Install Command artık `npm ci` olarak çalışır (Root Directory `web` olduğu için `web` içinde).

---

## 2. Netlify

1. [netlify.com](https://netlify.com) → GitHub ile giriş.
2. **Add new site** → **Import an existing project** → Repoyu seç.
3. Build ayarları:
   - **Base directory:** `web`
   - **Build command:** `npm run build`
   - **Publish directory:** `web/dist`
4. **Deploy site**.

Alternatif: Proje köküne `netlify.toml` ekleyin (aşağıda). Netlify bu dosyayı okuyacaktır.

---

## 3. Firebase Hosting

Projede zaten Firebase kullanıldığı için aynı projede hosting açabilirsiniz.

1. Firebase CLI:
   ```bash
   npm install -g firebase-tools
   firebase login
   ```
2. Hosting’i bağlamak (ilk kez):
   ```bash
   firebase init hosting
   ```
   - “Use an existing project” → projenizi seçin.
   - **Public directory:** `web/dist` (önce build alın).
   - Single-page app: **Yes**.
   - `dist/index.html`’i silmeyin (override sorusu varsa No).
3. Her deploy öncesi build, sonra deploy:
   ```bash
   cd web && npm run build && cd ..
   firebase deploy
   ```
   Sadece hosting:
   ```bash
   firebase deploy --only hosting
   ```

Not: “Public directory” için `web/dist` kullanıyorsanız, `firebase deploy` komutunu **repo kökünden** çalıştırın; Firebase `web/dist` içeriğini yükler.

---

## 4. GitHub Pages

1. Repo → **Settings** → **Pages** → Source: **GitHub Actions**.
2. `web/` için base path gerekiyor (örn. `https://kullanici.github.io/intyx-dynamic-widget/`).  
   `vite.config.js` içinde:
   ```js
   export default defineConfig({
     plugins: [react()],
     base: process.env.GITHUB_PAGES === 'true' ? '/intyx-dynamic-widget/' : '/',
     server: { port: 3000 },
   });
   ```
3. Workflow örneği: `.github/workflows/deploy-web.yml` (aşağıda).

---

## Ortam değişkenleri (API URL vb.)

Backend URL gibi değerler **web/src/config.js** veya env’den geliyorsa:

---

## Paddle için yapılacaklar

Web’de Pro/Enterprise ödemeleri Paddle ile çalışıyor. Canlıya almak için:

1. **Paddle hesabı**
   - [Paddle](https://www.paddle.com) → hesap açın.
   - Geliştirme için **Sandbox**, canlı ödeme için **Live** ortamını kullanın.

2. **Ürün ve fiyat (Price) oluşturma**
   - Dashboard → **Catalog** → **Products** → yeni product (örn. “Intyx Pro”, “Intyx Enterprise”).
   - Her plan için **Price** ekleyin (aylık/yıllık vs.) ve oluşan **Price ID**’yi (örn. `pri_01hxxx...`) not alın.

3. **API anahtarları**
   - **Developer tools** → **Authentication** (veya API keys bölümü).
   - **Client-side (publishable) token**’ı kopyalayın → `VITE_PADDLE_PUBLISHABLE_TOKEN` olarak kullanılacak.
   - Gerekirse backend/webhook için **Secret key** ayrı tutulur (şu an web’de sadece checkout kullanılıyor).

4. **Proje ortam değişkenleri**
   - **web** klasöründe veya deploy platformunda (Vercel/Netlify vb.) şunları tanımlayın:

   | Değişken | Açıklama | Örnek |
   |----------|----------|--------|
   | `VITE_PADDLE_ENV` | Ortam | `sandbox` veya `production` |
   | `VITE_PADDLE_PUBLISHABLE_TOKEN` | Paddle publishable key | `test_xxx` / `live_xxx` |
   | `VITE_PADDLE_PRICE_IDS` | Plan → Price ID eşlemesi (JSON) | `{"pro":"pri_01h...","enterprise":"pri_01j..."}` |

   - Yerel test: `web/.env` içine yazıp `npm run dev` ile deneyin.
   - Deploy’da: Vercel/Netlify **Environment Variables** ekranına aynı isimlerle ekleyin.

5. **Test**
   - Pricing sayfasında Pro veya Enterprise’a tıklayın → Paddle checkout açılmalı.
   - Sandbox’ta test kartlarıyla ödeme deneyin.

6. **İsteğe bağlı: Webhook**
   - Ödemeyi backend’de de doğrulamak isterseniz Paddle **Webhooks** bölümünden URL ekleyip (örn. `POST /api/paddle/webhook`) `transaction.completed` vb. event’leri işleyebilirsiniz. Şu an lisans oluşturma ödeme sonrası frontend’den yapılıyor.

---

## Ortam değişkenleri (API URL vb.)

Backend URL gibi değerler **web/src/config.js** veya env’den geliyorsa:

- **Vercel:** Project → Settings → Environment Variables.
- **Netlify:** Site → Site settings → Environment variables.
- **Firebase:** Build sırasında env kullanmak için `vite.config.js` içinde `define` veya `.env` kullanın; production’da farklı API URL’si için `.env.production` kullanabilirsiniz.

Build’den sonra `web/dist` içindeki dosyalar statik olduğu için runtime’da env okumak isterseniz `import.meta.env` (Vite) ile build-time’da inject edin.

---

## Özet

| Platform          | Base dir | Build        | Publish dir  |
|-------------------|----------|-------------|---------------|
| Vercel            | `web`    | `npm run build` | `dist`    |
| Netlify            | `web`    | `npm run build` | `web/dist` |
| Firebase Hosting   | —        | Önce `cd web && npm run build` | `web/dist` |
| GitHub Pages       | `web`    | `npm run build` (base: `/repo-adı/`) | `dist` |

En hızlı yol: GitHub repo bağlayıp **Vercel** veya **Netlify** ile import etmek; root directory’yi `web` yapıp build/publish ayarlarını yukarıdaki gibi vermek.
