# Firebase’de Aktive Edilecek Özellikler

**intyx-dynamic** projesi için Firebase Console’da açmanız gerekenler:

---

## 1. Firestore Database — **Zorunlu**

Backend (Flask) ve Flutter client veriyi burada tutuyor.

- [Firebase Console](https://console.firebase.google.com) → **intyx-dynamic** projesi
- Sol menü: **Build** → **Firestore Database** → **Create database**
- **Konum:** En yakın region seçin (örn. `europe-west1`)
- **Mod:** Başlangıç için “Start in **test mode**” (geliştirme); production’da kuralları deploy edin (aşağıda)

Oluşan koleksiyonlar (kod tarafından kullanılır, elle oluşturmanız gerekmez):

| Koleksiyon      | Açıklama                          |
|-----------------|-----------------------------------|
| `widgets`       | Widget tanımları                  |
| `trigger_rules` | Tetikleme kuralları               |
| `user_states`   | Kullanıcı durumu (dismissed, vb.)  |
| `data_cache`    | Önbellek (lisans, hava durumu vb.)|

---

## 2. Kurallar ve indeksler

Proje kökünde `firestore.rules` ve `firestore.indexes.json` var. Deploy için:

```bash
firebase use intyx-dynamic   # veya proje ID’niz
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
```

(İlk kez kullanıyorsanız `firebase init` ile Firestore’u seçip bu dosyaları bağlayın.)

---

## 3. Authentication — **İsteğe bağlı**

- **Ne zaman gerekir:** Flutter uygulamasında kullanıcı girişi (login) kullanıyorsanız ve Firestore kurallarındaki `user_states` okuma (`request.auth.uid == userId`) çalışsın istiyorsanız.
- **Ne zaman gerekmez:** Sadece backend API (Flask) ve anonim/API key ile çalışıyorsanız; backend service account ile yazar/okur, Auth açmanız gerekmez.

Açacaksanız: **Build** → **Authentication** → **Get started** → İstediğiniz yöntemi etkinleştirin (Email/Password, Google, vb.).

---

## 4. Açmanız gerekmeyenler

- **Realtime Database** — Kullanılmıyor (Firestore kullanılıyor).
- **Storage** — Kodda kullanılmıyor.
- **Cloud Functions** — Bu projede yok; isteğe bağlı.
- **Hosting** — İsteğe bağlı; web frontend Vercel/Netlify’da olabilir.

---

## 5. Backend (server) için Service Account

Backend’in Firestore’a yazabilmesi için:

- **Project settings** (dişli) → **Service accounts** → **Generate new private key**
- İndirilen JSON dosyasının yolunu `FIREBASE_CREDENTIALS_PATH` olarak kullanın (yerelde). Cloud Run’da boş bırakın; GCP Application Default Credentials kullanılır.

---

## Özet

| Özellik            | Durum        | Not                          |
|--------------------|-------------|------------------------------|
| **Firestore**      | Aktive et   | Veritabanı, zorunlu          |
| **Auth**           | İsteğe bağlı| Sadece client login varsa    |
| Realtime DB        | Gerek yok   | —                            |
| Storage            | Gerek yok   | —                            |
| Rules + Indexes    | Deploy et   | `firebase deploy --only firestore` |
