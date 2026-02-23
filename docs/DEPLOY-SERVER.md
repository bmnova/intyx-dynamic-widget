# Backend (server) Deploy Rehberi

Bu dokumanda **server/** (Flask) uygulamasinin buluta deploy edilmesi anlatiliyor. Once [API-KEYS.md](./API-KEYS.md) ile gerekli ortam degiskenlerini hazirlayin.

---

## Bilesenler Nerede Kosar?

| Bilesen | Nerede kosar | Not |
|---------|-------------|-----|
| **Flask API** | Cloud Run / Railway / Docker | Tum widget, license, AI, trend endpoint'leri |
| **Gemini API** | Google sunuculari | Sadece API key ile HTTP cagrisi |
| **MCP server** | Gelistirici makinesi (Cursor'in yaninda) | stdio, deploy edilmez |

### Gemini

Gemini, Google'in buluttaki API'si. Bizim kod sadece `GEMINI_API_KEY` ile HTTP uzerinden cagri yapar. Flask'i nereye deploy ederseniz Gemini cagrilari o ortamdan Google'a gider. Ayri bir Gemini sunucusu kurmak gerekmez.

### MCP Server

MCP server stdio ile calisan ayri bir process. Cursor/Claude Desktop gibi MCP client'lar bunu kendi subprocess'i olarak baslatir. **Buluta deploy edilmez**, gelistirici makinesinde calisir. Detay: [MCP-SERVER.md](./MCP-SERVER.md).

---

## 1. Google Cloud Run (onerilen)

Firebase kullandiginiz icin ayni GCP projesinde Cloud Run ile backend'i calistirabilirsiniz.

### On kosul

- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) yuklu ve `gcloud auth login` yapilmis
- GCP projeniz Firebase projesiyle ayni

### Adimlar

1. **Proje ve region secin**
   ```bash
   gcloud config set project YOUR_GCP_PROJECT_ID
   export REGION=europe-west1
   ```

2. **Container'i build edin ve push edin**
   ```bash
   # Ilk kez: API ve repo olusturma
   gcloud services enable artifactregistry.googleapis.com run.googleapis.com
   gcloud artifacts repositories create intyx-repo --repository-format=docker --location=$REGION

   # Build (repo kokunden)
   docker build -t $REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest .

   # Auth ve push
   gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
   docker push $REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest
   ```

3. **Cloud Run deploy**
   ```bash
   IMAGE=$REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest

   gcloud run deploy intyx-dynamic-widget \
     --image $IMAGE \
     --region $REGION \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars "FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID,GEMINI_API_KEY=YOUR_GEMINI_KEY,INTYX_SERVER_API_KEY=YOUR_SECRET_KEY"
   ```

   Opsiyonel env'leri de ekleyin:
   ```bash
   --set-env-vars "OPENWEATHER_API_KEY=xxx,NEWS_API_KEY=yyy,PADDLE_WEBHOOK_SECRET=zzz,SENTRY_DSN=sentry_dsn"
   ```

4. **URL'i alin**
   ```bash
   gcloud run services describe intyx-dynamic-widget --region $REGION --format 'value(status.url)'
   ```
   Bu URL'i web frontend'te `VITE_API_URL` olarak kullanin.

### Ortam degiskenleri ozeti (Cloud Run)

| Degisken | Zorunlu | Aciklama |
|----------|---------|----------|
| `FIREBASE_PROJECT_ID` | Evet | Firebase/GCP proje ID |
| `GEMINI_API_KEY` | Evet | AI widget onerileri ve agent gorevleri |
| `INTYX_SERVER_API_KEY` | Onerilen | API koruma anahtari |
| `FIREBASE_CREDENTIALS_PATH` | Hayir | Cloud Run'da bos birakin (ADC) |
| `OPENWEATHER_API_KEY` | Hayir | Hava durumu |
| `NEWS_API_KEY` | Hayir | Haber verisi |
| `TWITTER_BEARER_TOKEN` | Hayir | Trend verisi |
| `PADDLE_WEBHOOK_SECRET` | Hayir | Paddle odeme dogrulama |
| `SENTRY_DSN` | Hayir | Hata takip |

---

## 2. Railway / Render / Fly.io

Dockerfile kullanarak herhangi bir container platformunda calistirabilirsiniz.

- **Railway:** Repo baglayin → Dockerfile kullanin → Environment variables ekleyin → Deploy.
- **Render:** New → Web Service → Repo secin → Docker → Env vars ekleyin.
- **Fly.io:** `fly launch` → `fly secrets set FIREBASE_PROJECT_ID=... GEMINI_API_KEY=... INTYX_SERVER_API_KEY=...`

Firebase icin `FIREBASE_CREDENTIALS_PATH` kullanacaksaniz, service account JSON icerigini platformun "secret/file" ozelligiyle dosya olarak monte edin.

---

## 3. Yerel Test (Docker)

```bash
docker build -t intyx-server .
docker run -p 8080:8080 \
  -e FIREBASE_PROJECT_ID=intyx-dynamic-widget \
  -e GEMINI_API_KEY=your-gemini-key \
  -e INTYX_SERVER_API_KEY=test-key \
  intyx-server
```

Tarayicida `http://localhost:8080/api/health` → `{"status":"ok","service":"intyx-dynamic-widget"}` donmeli.

---

## 4. Yerel Test (Docker'siz)

```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env icine GEMINI_API_KEY yaz
python -m server.app
```

---

## 5. Deploy Sonrasi Kontrol

```bash
# Health check
curl https://YOUR_URL/api/health

# Lisans olustur (public endpoint)
curl -X POST https://YOUR_URL/api/licenses \
  -H "Content-Type: application/json" \
  -d '{"plan":"starter"}'

# Auth ile istek (server key)
curl https://YOUR_URL/api/widgets \
  -H "Authorization: Bearer YOUR_INTYX_SERVER_API_KEY"

# Auth ile istek (license key)
curl https://YOUR_URL/api/widgets \
  -H "Authorization: Bearer intyx_xxxxx"
```

Eksik key'ler icin log'larda uyari goreceksiniz. Tum key'lerin listesi: [API-KEYS.md](./API-KEYS.md).

---

## Dockerfile Detay

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY server/requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt
COPY server/ ./server/
ENV PORT=8080
EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 4 server.app:app --capture-output
```

- Gunicorn ile production-grade WSGI
- 1 worker, 4 thread (Cloud Run icin yeterli — scale horizontally)
- `server.app:app` — Flask app entry point
