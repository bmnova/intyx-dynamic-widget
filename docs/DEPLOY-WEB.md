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
Önizleme: `npm run preview` (genelde http://localhost:4173)

---

## 1. Vercel (önerilen, GitHub ile)

1. [vercel.com](https://vercel.com) → GitHub ile giriş.
2. **Add New Project** → Repoyu seç (`intyx-dynamic-widget`).
3. **Framework Preset:** Listeden **Vite** seçin (gerekli; aksi halde build ayarları yanlış olur).
4. **Root Directory:** `web` (Edit / Browse ile `web` klasörünü seçin).
5. Build Command / Output Directory boş bırakılabilir; `web/vercel.json` otomatik kullanılır.
6. **Deploy** → Her `main` push’unda otomatik deploy olur.

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
