# Firebase Kurulum Rehberi

**intyx-dynamic-widget** projesi icin Firebase Console'da yapilmasi gerekenler.

---

## 1. Firestore Database — Zorunlu

Backend (Flask) ve Flutter client veriyi burada tutuyor.

- [Firebase Console](https://console.firebase.google.com) → projenizi secin (veya yeni olusturun)
- Sol menu: **Build** → **Firestore Database** → **Create database**
- **Konum:** En yakin region (orn. `europe-west1`)
- **Mod:** Baslangic icin "Start in test mode"; production'da kurallari deploy edin

### Koleksiyonlar

Kod tarafindan otomatik olusturulur, elle olusturmaniz gerekmez:

| Koleksiyon | Aciklama | Kullanim |
|-----------|----------|----------|
| `widgets` | Widget tanimlari | Widget CRUD API |
| `trigger_rules` | Tetikleme kurallari | Trigger evaluation |
| `user_states` | Kullanici durumlari (dismissed, interactions, user_actions) | Widget dismiss/interact |
| `data_cache` | Onbellek (hava durumu, haberler, burclar, trendler) | Data source polling |
| `licenses` | Lisans kayitlari | Lisans olusturma/dogrulama |
| `agent_tasks` | Agent task/persona kayitlari | Agent task CRUD |

---

## 2. Guvenlik Kurallari ve Index'ler

Proje kokunde `firestore.rules` ve `firestore.indexes.json` dosyalari mevcut.

### Deploy

```bash
npm install -g firebase-tools  # ilk kez
firebase login
firebase use YOUR_PROJECT_ID

# Kurallari deploy et
firebase deploy --only firestore:rules

# Index'leri deploy et
firebase deploy --only firestore:indexes
```

### Kurallar Ozeti

```
widgets          → read: herkes, write: sadece server (Admin SDK)
trigger_rules    → read: herkes, write: sadece server
user_states      → read: sadece sahibi (auth.uid == userId), write: sadece server
data_cache       → read: herkes, write: sadece server
licenses         → read/write: sadece server
agent_tasks      → read/write: sadece server
```

Backend Firebase Admin SDK ile calisir — Admin SDK tum kurallari bypass eder. Kurallar sadece client-side (Flutter/web) erisimleri icin gecerlidir.

---

## 3. Authentication — Istege Bagli

### Ne zaman gerekir?
- Flutter uygulamasinda kullanici girisi (login) kullaniyorsaniz
- Firestore kurallarindaki `user_states` okuma (`request.auth.uid == userId`) calissin istiyorsaniz

### Ne zaman gerekmez?
- Sadece backend API (Flask) ve API key ile calisiyorsaniz
- Backend service account ile yazar/okur, Auth acmaniz gerekmez

Acacaksaniz: **Build** → **Authentication** → **Get started** → Yontemi etkinlestirin (Email/Password, Google, vb.).

---

## 4. Service Account (Backend icin)

Backend'in Firestore'a yazabilmesi icin:

### Yerel gelistirme
1. Firebase Console → **Project settings** (disli) → **Service accounts** → **Generate new private key**
2. Indirilen JSON dosyasinin yolunu `FIREBASE_CREDENTIALS_PATH` olarak `.env`'e yazin

### Cloud Run / GCP
- Bos birakin — Application Default Credentials (ADC) otomatik kullanilir
- Cloud Run service account'a Firestore erisim izni verin (varsayilan olarak var)

### Diger platformlar (Railway, Render, Fly.io)
- Service account JSON icerigini platformun secret/file ozelligiyle monte edin
- Veya JSON'i base64 encode edip env var olarak saklayip decode edin

---

## 5. Acmaniz Gerekmeyenler

| Ozellik | Durum | Not |
|---------|-------|-----|
| **Realtime Database** | Gerek yok | Firestore kullaniliyor |
| **Storage** | Gerek yok | Kodda kullanilmiyor |
| **Cloud Functions** | Istege bagli | Bkz. [FIREBASE-FUNCTIONS-GEMINI.md](./FIREBASE-FUNCTIONS-GEMINI.md) |
| **Hosting** | Istege bagli | Web frontend Vercel/Netlify'da olabilir |

---

## 6. Ozet

| Adim | Yapilacak |
|------|-----------|
| 1 | Firestore Database olustur |
| 2 | Service account JSON indir (yerel icin) |
| 3 | `FIREBASE_PROJECT_ID` ve `FIREBASE_CREDENTIALS_PATH` env'lere yaz |
| 4 | `firebase deploy --only firestore:rules` |
| 5 | `firebase deploy --only firestore:indexes` |
| 6 | Server'i calistir, koleksiyonlar otomatik olusur |
