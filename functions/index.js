/**
 * Firebase Cloud Functions — Gemini widget suggestion & content generation.
 * Deploy: firebase deploy --only functions
 * Env: GEMINI_API_KEY (Firebase Console > Functions > Environment variables veya Secret Manager)
 */

import { onRequest } from "firebase-functions/v2/https";
import { GoogleGenerativeAI } from "@google/generative-ai";

const GEMINI_MODEL = "gemini-2.0-flash";

const WIDGET_CATALOG = {
  widgets: [
    { type: "title_subtitle_image", description: "Baslik, alt baslik ve resim iceren kart", params: ["title", "subtitle", "image_url", "image_fit"] },
    { type: "clickable_image_link", description: "Tiklanabilir resim, baslik ve yonlendirme linki", params: ["title", "image_url", "link_url", "link_text"] },
    { type: "hero_image", description: "Tam genislikte hero resim, overlay baslik ve CTA butonu", params: ["title", "image_url", "button_text", "button_action"] },
    { type: "icon_text_action", description: "Ikon, baslik, aciklama ve aksiyon butonu", params: ["icon", "title", "description", "action_text", "action_url"] },
    { type: "countdown_banner", description: "Geri sayim zamanlayici ile kampanya banner'i", params: ["title", "end_time", "button_text", "button_action"] },
    { type: "carousel", description: "Yatay kaydirmali coklu icerik karti", params: ["title", "items"] },
    { type: "promotional", description: "Kampanya/promosyon karti", params: ["title", "description", "image_url", "badge_text", "action_url"] },
    { type: "contextual", description: "Baglamsal bilgi karti (hava durumu, burc vs.)", params: ["title", "content", "icon", "source"] },
    { type: "informational", description: "Bilgilendirme/duyuru karti", params: ["title", "message", "severity"] },
    { type: "functional", description: "Aksiyon odakli kart - buton(lar)", params: ["title", "actions"] },
    { type: "rating", description: "Yildiz puanlama karti", params: ["title", "subtitle", "max_stars"] },
    { type: "poll", description: "Anket/oylama karti", params: ["question", "options"] },
    { type: "social_proof", description: "Sosyal kanit", params: ["title", "subtitle", "metric", "metric_label", "quote", "author"] },
    { type: "progress", description: "Ilerleme/hedef karti", params: ["title", "subtitle", "progress", "progress_label", "action_text"] },
    { type: "profile", description: "Profil/kullanici spotlight karti", params: ["name", "avatar_url", "title", "subtitle", "action_text"] },
    { type: "banner", description: "Basit metin banner", params: ["text", "emoji", "action_text", "style"] },
  ],
};

const SYSTEM_PROMPT = `Sen bir mobil uygulama widget onerme asistanisin.
Kullanicinin context'ine (hava durumu, konum, zaman, kullanici davranislari vs.) gore hangi widget'larin gosterilmesi gerektigine karar verirsin.

Mevcut widget katalogu:
{CATALOG}

Eger context icinde "developer_task" alani varsa, bu developerin verdigi gorev tanimidir. Bu goreve gore en uygun widget tipini sec ve parametreleri doldur.
Eger context icinde "viral_trends" varsa, trendleri kullanarak hero_image veya promotional widget'larla kartlar olustur.
Eger context icinde color_palette varsa, widget'larin common alanina aynen ekle.

Yanit olarak SADECE gecerli JSON dondur, baska bir sey yazma.
JSON formati:
{
  "widgets": [
    {
      "id": "w_<unique>",
      "type": "<widget_type>",
      "params": { ... },
      "common": { "dismissible": true, "priority": 10, "ttl_seconds": 3600, "color_palette": { ... } }
    }
  ]
}`;

function stripCodeFences(text) {
  let t = (text || "").trim();
  if (t.startsWith("```")) {
    const idx = t.indexOf("\n");
    t = idx !== -1 ? t.slice(idx + 1) : t.replace(/^`+/, "");
  }
  if (t.endsWith("```")) t = t.slice(0, -3);
  return t.trim();
}

function getModel() {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw new Error("GEMINI_API_KEY not set. Set in Firebase Console > Functions > Environment variables or use Secret Manager.");
  const genAI = new GoogleGenerativeAI(key);
  return genAI.getGenerativeModel({ model: GEMINI_MODEL });
}

/**
 * POST body: { context: object }
 * Response: { widgets: [...], error?: string }
 */
export const suggestWidget = onRequest(
  { cors: true },
  async (req, res) => {
    if (req.method !== "POST") {
      res.status(405).json({ error: "Method not allowed" });
      return;
    }
    const body = req.body || {};
    const context = body.context ?? body;
    if (!context || typeof context !== "object") {
      res.status(400).json({ error: "Context required" });
      return;
    }
    try {
      const model = getModel();
      const catalogStr = JSON.stringify(WIDGET_CATALOG, null, 2);
      const system = SYSTEM_PROMPT.replace("{CATALOG}", catalogStr);
      const prompt = `Kullanici context'i:\n${JSON.stringify(context, null, 2)}\n\nBu context'e uygun widget'lari oner.`;
      const result = await model.generateContent(system + "\n\n" + prompt);
      const text = result.response?.text?.() ?? "";
      const parsed = JSON.parse(stripCodeFences(text));
      res.status(200).json(parsed);
    } catch (e) {
      console.error("suggestWidget failed", e);
      res.status(500).json({ widgets: [], error: "AI suggestion failed" });
    }
  }
);

/**
 * POST body: { widget_type: string, context: object }
 * Response: { type, params } | { error }
 */
export const generateWidgetContent = onRequest(
  { cors: true },
  async (req, res) => {
    if (req.method !== "POST") {
      res.status(405).json({ error: "Method not allowed" });
      return;
    }
    const body = req.body || {};
    const widgetType = body.widget_type;
    const context = body.context || {};
    if (!widgetType) {
      res.status(400).json({ error: "widget_type required" });
      return;
    }
    const entry = WIDGET_CATALOG.widgets.find((w) => w.type === widgetType);
    if (!entry) {
      res.status(400).json({ error: `Unknown widget type: ${widgetType}` });
      return;
    }
    try {
      const model = getModel();
      const prompt = `'${widgetType}' tipi widget icin icerik uret.\nWidget aciklamasi: ${entry.description}\nKullanilabilir parametreler: ${JSON.stringify(entry.params)}\nContext: ${JSON.stringify(context, null, 2)}\n\nSadece bu widget'in params degerlerini JSON olarak dondur.`;
      const result = await model.generateContent(prompt);
      const text = result.response?.text?.() || "";
      const params = JSON.parse(stripCodeFences(text));
      res.status(200).json({ type: widgetType, params });
    } catch (e) {
      console.error("generateWidgetContent failed", e);
      res.status(500).json({ error: "Content generation failed" });
    }
  }
);
