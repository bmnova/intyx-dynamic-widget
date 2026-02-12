# Backend (server) deploy rehberi

Bu dokümanda **server/** (Flask) uygulamasının buluta deploy edilmesi anlatılıyor. Önce [API-KEYS.md](./API-KEYS.md) ile gerekli ortam değişkenlerini hazırlayın.

---

## Gemini ve MCP nerede koşar?

### Gemini

**Gemini**, Google’ın buluttaki bir API’si; kendi sunucularında çalışır. Bizim kod sadece `GEMINI_API_KEY` ile HTTP üzerinden çağrı yapar.

- **Gemini’yi kim kullanıyor?** Flask uygulaması (widget önerisi, agent görevleri, trendler) ve MCP server (tool’lar).
- **Nerede koşar?** Flask’ı nereye deploy ederseniz (Cloud Run, Railway, vb.) Gemini çağrıları **o ortamdan** Google’a gider. Ayrı bir “Gemini sunucusu” kurmanız gerekmez; sadece deploy ettiğiniz backend’e `GEMINI_API_KEY` env’ini verin.

### MCP server

**MCP server** (Model Context Protocol) stdio ile çalışan **ayrı bir process**. Cursor / Claude Desktop gibi MCP client’lar bunu kendi subprocess’i olarak başlatır.

- **Nerede koşar?** MCP server buluta deploy edilmez. **Cursor’ın (veya kullandığınız IDE’nin) çalıştığı makinede** çalışır. Cursor, `mcp_config` içindeki tanıma göre `python -m server.mcp` komutunu çalıştırır ve stdin/stdout üzerinden konuşur.
- **Tek sunucu, tüm araçlar:** `server.mcp` tek MCP sunucusu; içinde **Firebase** (widgets, trigger rules, data cache, trends), **Weather** (get_current_weather, get_weather_forecast, get_weather_by_coords), **Holidays** (get_today_holidays, get_upcoming_holidays, suggest_widget_for_holiday, vb.) ve **Gemini orkestrasyonu** (tool: **ask**) vardır. `ask` ile doğal dilde soru sorarsınız; Gemini gerekirse weather, Firebase ve holidays araçlarını kendisi çağırıp cevabı birleştirir.
- **Gereksinimler:** Python, proje kodu, env: `FIREBASE_PROJECT_ID`, `GEMINI_API_KEY` (zorunlu), isteğe bağlı `FIREBASE_CREDENTIALS_PATH`, `OPENWEATHER_API_KEY` (weather için). Örnek: proje kökündeki `mcp_config.example.json` → Cursor MCP ayarlarına kopyalayıp `cwd` ve `env` değerlerini düzenleyin.

| Bileşen | Nerede koşar | Not |
|--------|----------------|-----|
| **Gemini API** | Google sunucuları | Sadece API key ile çağrı |
| **Gemini kullanan kod** | Flask ile aynı yerde (Cloud Run vb.) | Backend deploy edildiği yerde |
| **MCP server** | Geliştirici makinesi (Cursor’ın yanında) | stdio, deploy edilmez |

**Alternatif:** Gemini’yi **Firebase Cloud Functions** içinde çalıştırmak isterseniz bkz. [FIREBASE-FUNCTIONS-GEMINI.md](./FIREBASE-FUNCTIONS-GEMINI.md). O zaman AI endpoint’leri Firebase’de koşar; Flask sadece widget/license API’lerinde kalabilir.

---

## 1. Google Cloud Run (önerilen)

Firebase kullandığınız için aynı GCP projesinde Cloud Run ile backend’i çalıştırabilirsiniz. **FIREBASE_CREDENTIALS_PATH** vermenize gerek yok; Cloud Run ortamında Application Default Credentials kullanılır.

### Ön koşul

- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) yüklü ve `gcloud auth login` yapılmış olsun.
- GCP projeniz Firebase projesiyle aynı olsun (veya `FIREBASE_PROJECT_ID` ile Firebase proje ID’sini verin).

### Adımlar

1. **Proje ve region seçin**
   ```bash
   gcloud config set project YOUR_GCP_PROJECT_ID
   export REGION=europe-west1
   ```

2. **Container’ı build edin ve Artifact Registry’e push edin**
   ```bash
   # İlk kez: Artifact Registry API ve repo oluşturma
   gcloud services enable artifactregistry.googleapis.com run.googleapis.com
   gcloud artifacts repositories create intyx-repo --repository-format=docker --location=$REGION

   # Build (repo kökünden)
   docker build -t $REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest .

   # Auth ve push
   gcloud auth configure-docker $REGION-docker.pkg.dev --quiet
   docker push $REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest
   ```

3. **Cloud Run servisini deploy edin**
   ```bash
   IMAGE=$REGION-docker.pkg.dev/$(gcloud config get-value project)/intyx-repo/intyx-server:latest

   gcloud run deploy intyx-dynamic-widget \
     --image $IMAGE \
     --region $REGION \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars "FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID,GEMINI_API_KEY=YOUR_GEMINI_KEY"
   ```

   **TODO:** Test sonrası `INTYX_SERVER_API_KEY` ekleyin (API koruma).

   İsteğe bağlı env’leri de ekleyin (virgülle ayırarak tek `--set-env-vars` veya ayrı ayrı):
   ```bash
   --set-env-vars "OPENWEATHER_API_KEY=xxx"
   ```

   **Sadece kimlik doğrulamalı erişim** isterseniz `--allow-unauthenticated` kaldırıp `--no-allow-unauthenticated` kullanın.

4. **URL’i alın**
   ```bash
   gcloud run services describe intyx-dynamic-widget --region $REGION --format 'value(status.url)'
   ```
   Bu URL’i web frontend’te `VITE_API_URL` olarak kullanın.

### Ortam değişkenleri özeti (Cloud Run)

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `FIREBASE_PROJECT_ID` | Evet | Firebase/GCP proje ID |
| `GEMINI_API_KEY` | Evet | AI widget önerileri ve agent görevleri |
| `INTYX_SERVER_API_KEY` | TODO (test sonrası) | API koruma anahtarı — şimdilik atlanıyor |
| `FIREBASE_CREDENTIALS_PATH` | Hayır | Cloud Run’da boş bırakın (ADC kullanılır) |
| `OPENWEATHER_API_KEY` | Hayır | Hava durumu |
| `TWITTER_BEARER_TOKEN` | Hayır | Trend verisi |

---

## 2. Railway / Render / Fly.io

Dockerfile kullanarak herhangi bir container platformunda da çalıştırabilirsiniz.

- **Railway:** Repo bağlayın → Root directory boş, Dockerfile’ı kullanın → Environment variables ekleyin → Deploy.
- **Render:** New → Web Service → Repo seçin → Docker → Env vars ekleyin.
- **Fly.io:** `fly launch` → Dockerfile otomatik seçilir → `fly secrets set FIREBASE_PROJECT_ID=... GEMINI_API_KEY=...` ile key’leri verin. (TODO: Test sonrası `INTYX_SERVER_API_KEY` ekleyin.)

Firebase için **FIREBASE_CREDENTIALS_PATH** kullanacaksanız, service account JSON içeriğini platformun “secret / file” özelliğiyle dosya olarak monte edin veya JSON’ı base64 ile env’e koyup uygulama başlangıcında dosyaya yazan küçük bir script kullanın (güvenliği platform dokümantasyonuna göre ayarlayın).

---

## 3. Yerel test (Docker)

```bash
docker build -t intyx-server .
docker run -p 8080:8080 \
  -e FIREBASE_PROJECT_ID=intyx-dynamic-widget \
  -e INTYX_SERVER_API_KEY=test-key \
  intyx-server
```

Tarayıcıda `http://localhost:8080/api/health` → `{"status":"ok",...}` dönmeli.

---

## 4. Aktive etme kontrolü

Deploy sonrası:

1. **Health:** `curl https://YOUR_CLOUD_RUN_URL/api/health`
2. **Lisans (auth yoksa):** `curl -X POST https://YOUR_URL/api/licenses -H "Content-Type: application/json" -d '{"plan":"starter"}'`
3. **Auth varken:** `Authorization: Bearer YOUR_INTYX_SERVER_API_KEY` header’ı ile istek atın.

Eksik key’ler için log’larda uyarı göreceksiniz (weather placeholder, AI unavailable vb.). Tüm key’lerin listesi için [API-KEYS.md](./API-KEYS.md) dosyasına bakın.
