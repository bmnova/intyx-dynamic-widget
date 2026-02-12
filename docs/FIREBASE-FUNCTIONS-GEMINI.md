# Gemini — Firebase Cloud Functions olarak çalıştırma

Gemini kullanan AI endpoint’lerini (**widget önerisi**, **içerik üretimi**) Flask yerine **Firebase Cloud Functions** içinde çalıştırabilirsiniz. Böylece Gemini kodu Firebase tarafında koşar; Flask sadece widget/trigger/license API’lerine odaklanır.

---

## Ne var?

- **`functions/`** — Node.js 18, Firebase Functions v2
  - **suggestWidget** — POST ile `{ context }` alır, Gemini ile widget listesi döner (Flask `/api/ai/suggest-widget` ile aynı sözleşme).
  - **generateWidgetContent** — POST ile `{ widget_type, context }` alır, widget params döner (Flask `/api/ai/generate-content` ile aynı).

- **`firebase.json`** — Functions kaynağı `functions/` olacak şekilde ayarlı.

---

## Deploy

1. **Firebase CLI ve proje**
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase use intyx-dynamic   # veya kendi proje ID'niz
   ```

2. **Functions bağımlılıkları**
   ```bash
   cd functions
   npm install
   cd ..
   ```

3. **GEMINI_API_KEY**
   - **Seçenek A:** Firebase Console → **Build** → **Functions** → İlgili function → **Environment variables** → `GEMINI_API_KEY` ekleyin (deploy sonrası).
   - **Seçenek B:** Google Cloud Console → **Secret Manager** → secret oluştur (örn. `GEMINI_API_KEY`). Sonra Functions’ta bu secret’ı kullanacak şekilde ayarlayın (Firebase dokümantasyonu: “Secret Manager ile Cloud Functions”).
   - **Seçenek C (yerel test):** `functions/.env` içine `GEMINI_API_KEY=...` yazın (Firebase emulator env’i okuyabilir).

4. **Deploy**
   ```bash
   firebase deploy --only functions
   ```
   Çıktıda URL’ler görünecek, örneğin:
   - `https://<region>-<project>.cloudfunctions.net/suggestWidget`
   - `https://<region>-<project>.cloudfunctions.net/generateWidgetContent`

---

## Flask’tan kullanım (opsiyonel)

Gemini’yi artık Cloud Functions’ta çalıştırmak istiyorsanız, Flask’taki `/api/ai/*` route’larını bu URL’lere proxy’leyebilir veya client doğrudan Functions URL’ine istek atar.

**Örnek: Flask’ta proxy**

Env’e ekleyin:
```bash
# Cloud Functions URL’leri (deploy sonrası alın)
GEMINI_SUGGEST_URL=https://<region>-<project>.cloudfunctions.net/suggestWidget
GEMINI_GENERATE_URL=https://<region>-<project>.cloudfunctions.net/generateWidgetContent
```

Flask’ta `routes/ai.py` içinde: istek gövdesini alıp bu URL’lere POST atıp cevabı döndürürsünüz (ve isteğe bağlı `INTYX_SERVER_API_KEY` ile sadece kendi backend’inizin çağırmasına izin verirsiniz). Bu değişiklik ayrı bir adım olarak yapılabilir; şu an Functions bağımsız çalışır.

---

## Özet

| Bileşen | Nerede koşar |
|--------|----------------|
| **suggestWidget / generateWidgetContent** | Firebase Cloud Functions (Google’da) |
| **GEMINI_API_KEY** | Firebase/Cloud Console env veya Secret Manager |
| **Flask** | İsterseniz aynen Cloud Run’da; AI isteklerini Functions’a yönlendirebilir veya client doğrudan Functions’ı çağırır. |

Test için:
```bash
curl -X POST "https://<your-function-url>/suggestWidget" \
  -H "Content-Type: application/json" \
  -d '{"context":{"developer_task":"Kullaniciya hava durumuna gore oneri goster"}}'
```
