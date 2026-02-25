"""Gemini AI client for widget suggestion and content generation."""

from __future__ import annotations

import datetime
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from server.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def _enrich_context(context: dict[str, Any]) -> dict[str, Any]:
    """Auto-inject all available cached/live data into the widget context.

    This ensures Gemini always has real weather, news, trends, and holiday
    data to work with — preventing it from fabricating dummy content.
    """
    enriched = dict(context)

    now = datetime.datetime.now()
    enriched.setdefault("current_date", now.strftime("%Y-%m-%d"))
    enriched.setdefault("current_time", now.strftime("%H:%M"))
    enriched.setdefault("season", _season(now.month))

    try:
        from server import firebase_client as fb  # local import to avoid circular deps

        # ── Weather ──────────────────────────────────────────────────────
        if "weather" not in enriched:
            weather_cache = fb.get_cached_data("weather")
            if weather_cache:
                enriched["weather"] = {
                    "location": weather_cache.get("location"),
                    "temperature_c": weather_cache.get("temperature"),
                    "condition": weather_cache.get("condition"),
                    "humidity": weather_cache.get("humidity"),
                }

        # ── News headlines (top 5) ────────────────────────────────────────
        if "news_headlines" not in enriched:
            news_cache = fb.get_cached_data("news")
            if news_cache:
                items = news_cache.get("items", [])[:5]
                if items:
                    enriched["news_headlines"] = [
                        {"title": i.get("headline", ""), "source": i.get("source", "")}
                        for i in items
                    ]

        # ── Viral trends (top 5 by engagement) ───────────────────────────
        if "viral_trends" not in enriched:
            trends_cache = fb.get_cached_data("trends")
            if trends_cache:
                items = trends_cache.get("items", [])[:5]
                if items:
                    enriched["viral_trends"] = [
                        {
                            "title": t.get("title", ""),
                            "platform": t.get("platform", ""),
                            "category": t.get("category", ""),
                            "engagement": t.get("engagement", 0),
                            "image_url": t.get("image_url", ""),
                        }
                        for t in items
                    ]

        # ── Today's holidays ─────────────────────────────────────────────
        if "today_holidays" not in enriched:
            from server.mcp.holidays.data import ALL_HOLIDAYS
            today_holidays = [
                d.to_dict()
                for d in ALL_HOLIDAYS
                if d.date[0] == now.month and d.date[1] == now.day
            ]
            if today_holidays:
                enriched["today_holidays"] = today_holidays

    except Exception:
        logger.debug("Context enrichment partially failed — continuing with available data")

    return enriched

WIDGET_CATALOG = {
    "widgets": [
        {
            "type": "title_subtitle_image",
            "description": "Baslik, alt baslik ve resim iceren kart",
            "params": ["title", "subtitle", "image_url", "image_fit"],
        },
        {
            "type": "clickable_image_link",
            "description": "Tiklanabilir resim, baslik ve yonlendirme linki",
            "params": ["title", "image_url", "link_url", "link_text"],
        },
        {
            "type": "hero_image",
            "description": "Tam genislikte hero resim, overlay baslik ve CTA butonu",
            "params": ["title", "image_url", "button_text", "button_action"],
        },
        {
            "type": "icon_text_action",
            "description": "Ikon, baslik, aciklama ve aksiyon butonu",
            "params": ["icon", "title", "description", "action_text", "action_url"],
        },
        {
            "type": "countdown_banner",
            "description": "Geri sayim zamanlayici ile kampanya banner'i",
            "params": ["title", "end_time", "button_text", "button_action"],
        },
        {
            "type": "carousel",
            "description": "Yatay kaydirmali coklu icerik karti",
            "params": ["title", "items"],
        },
        {
            "type": "promotional",
            "description": "Kampanya/promosyon karti",
            "params": ["title", "description", "image_url", "badge_text", "action_url"],
        },
        {
            "type": "contextual",
            "description": "Baglamsal bilgi karti (hava durumu, burc vs.)",
            "params": ["title", "content", "icon", "source"],
        },
        {
            "type": "informational",
            "description": "Bilgilendirme/duyuru karti",
            "params": ["title", "message", "severity"],
        },
        {
            "type": "functional",
            "description": "Aksiyon odakli kart - buton(lar)",
            "params": ["title", "actions"],
        },
        {
            "type": "rating",
            "description": "Yildiz puanlama karti — deneyim degerlendirmesi",
            "params": ["title", "subtitle", "max_stars"],
        },
        {
            "type": "poll",
            "description": "Anket/oylama karti — tek secimli",
            "params": ["question", "options"],
        },
        {
            "type": "social_proof",
            "description": "Sosyal kanit — metrik, testimonial, kullanici sayisi",
            "params": ["title", "subtitle", "metric", "metric_label", "quote", "author"],
        },
        {
            "type": "progress",
            "description": "Ilerleme/hedef karti — yuzde cubugu ile",
            "params": ["title", "subtitle", "progress", "progress_label", "action_text"],
        },
        {
            "type": "profile",
            "description": "Profil/kullanici spotlight karti",
            "params": ["name", "avatar_url", "title", "subtitle", "action_text"],
        },
        {
            "type": "banner",
            "description": "Basit metin banner — ozel gun, duyuru, motivasyon",
            "params": ["text", "emoji", "action_text", "style"],
        },
    ],
}

VALID_WIDGET_TYPES = {w["type"] for w in WIDGET_CATALOG["widgets"]}

SYSTEM_PROMPT = """Sen bir mobil uygulama widget oneri asistanisin.
Kullanicinin context'ine gore hangi widget'larin gosterilmesi gerektigine karar verirsin.

Mevcut widget katalogu:
{catalog}

━━━ TEMEL KURAL: GERCEK VERIYI KULLAN ━━━

Context icindeki her alan GERCEK, canli verilerdir. Su kurallara KESINLIKLE uy:

• "weather" varsa → sicaklik ve durumu widget basligina/icerigine birebir yaz.
  DOGRU: "Istanbul'da 8°C, karli — icerde kal"
  YANLIS: "Hava durumuna gore giyinin" (muglak, sahte)

• "news_headlines" varsa → gercek bir manset sec, onu contextual/banner widgeta koy.
  DOGRU: title = mansetin kendisi, source = kaynak adi
  YANLIS: "Bugunun gelismeleri" (uydurma)

GORSEL URL KURALI (KRITIK):
  - image_url ASLA kendin uretme veya tahminde bulunma.
  - image_url degerini SADECE context'teki trend nesnesinin "image_url" alanindan al.
  - Eger trendin "image_url" alani bos ("") veya yoksa, widget params'ina image_url EKLEME.
  - "https://example.com/...", "https://via.placeholder.com/..." gibi sahte URL'ler YASAK.

Eger context icinde color_palette varsa, widget'larin common alanina aynen ekle.
Bu sayede widget'lar host uygulamanin renk temasina uyumlu gorunur.

• "viral_trends" varsa → en yuksek engagement'li trendi hero_image/promotional widgeta donustur.
  title = trendin tam adi, button_action = "app://explore?trend=<trend_title>"

• "today_holidays" varsa → o gun icin tematik bir widget MUTLAKA ekle.

• "season" varsa → butun widget icerikleri o mevsime uygun olmali.

━━━ KESINLIKLE YASAK OLAN SEYLER ━━━

✗ Sahte ilerleme yuzdesi: "Bugun hedefinizin %73'une ulastiniz!" (uydurmaca)
✗ Sahte motivasyon sozu: "Basari cesur olanlarin..." (uydurmaca)
✗ Sahte istatistik: "Bu hafta 12.450 adim attin" (uydurmaca)
✗ Progress widget — context'te gercek bir ilerleme degeri YOKSA kullanma.
✗ Profile widget — context'te gercek kullanici adi/avatari YOKSA kullanma.
✗ Sahte social_proof metrigi: "50.000 kullanici bu widget'i begendi" (uydurmaca)

━━━ DEVELOPER TASK ━━━

"developer_task" alani developer'in uygulamasini ve istegini tanimlar.
Bu goreve gore en uygun widget tipini sec. App amacina uygun icerik olustur —
ama icerigi GERCEK veriden (hava, haber, trend, ozel gun) devsireceksin.

━━━ VIRAL TRENDLER ━━━

Her trend: {{ "title": "...", "platform": "...", "category": "...", "engagement": 500000 }}
- App amacina uygun trendleri sec
- Yuksek engagement'li (>100k) trendlere priority: 10 ver
- button_action: "app://explore?trend=<trend_title>"

━━━ RENK PALETI ━━━

"color_palette" varsa tum widget'larin common.color_palette alanina ekle.

━━━ CIKTI FORMATI ━━━

SADECE gecerli JSON dondur, baska hicbir sey yazma:
{{
  "widgets": [
    {{
      "id": "w_<unique_6_char>",
      "type": "<widget_type>",
      "params": {{ ... }},
      "common": {{
        "dismissible": true,
        "priority": 5,
        "ttl_seconds": 3600,
        "color_palette": {{}}
      }}
    }}
  ]
}}
"""


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences from AI response, handling edge cases."""
    text = text.strip()
    # Handle ```json or ``` at the start
    if text.startswith("```"):
        # Find the end of the first line (could be ```json, ```JSON, just ```)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        else:
            # No newline — the whole thing is just ``` with no content
            return text.lstrip("`")
    # Strip trailing ```
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class GeminiClient:
    """Wrapper around Google GenAI SDK for widget operations.

    Use get_gemini_client() for a shared singleton instance.
    """

    def __init__(self) -> None:
        self._client = genai.Client(api_key=GEMINI_API_KEY or None)

    def suggest_widgets(self, context: dict[str, Any]) -> dict[str, Any]:
        """Suggest widgets based on user context.

        Context is automatically enriched with live cached data (weather,
        news, trends, holidays) so that Gemini generates grounded widgets
        instead of fabricated dummy content.
        """
        enriched = _enrich_context(context)
        system = SYSTEM_PROMPT.format(catalog=json.dumps(WIDGET_CATALOG, indent=2))
        prompt = (
            f"Kullanici context'i (canli, gercek veriler iceriyor):\n"
            f"{json.dumps(enriched, indent=2, ensure_ascii=False)}\n\n"
            f"Bu context'e uygun widget'lari oner. "
            f"Context'teki GERCEK verileri kullan, asla icerik uydurma."
        )

        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=system),
            )
            text = _strip_code_fences(response.text)
            result = json.loads(text)
            # Tag response with which real data was injected for debugging
            result["_enriched_with"] = [
                k for k in ("weather", "news_headlines", "viral_trends", "today_holidays")
                if k in enriched
            ]
            return result
        except Exception:
            logger.exception("Gemini suggest_widgets failed")
            return {"widgets": [], "error": "AI suggestion failed"}

    def generate_widget_content(
        self, widget_type: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate content for a specific widget type."""
        catalog_entry = next(
            (w for w in WIDGET_CATALOG["widgets"] if w["type"] == widget_type),
            None,
        )
        if not catalog_entry:
            return {"error": f"Unknown widget type: {widget_type}"}

        prompt = (
            f"'{widget_type}' tipi widget icin icerik uret.\n"
            f"Widget aciklamasi: {catalog_entry['description']}\n"
            f"Kullanilabilir parametreler: {catalog_entry['params']}\n"
            f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
            f"Sadece bu widget'in params degerlerini JSON olarak dondur."
        )

        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
            )
            text = _strip_code_fences(response.text)
            params = json.loads(text)
            return {"type": widget_type, "params": params}
        except Exception:
            logger.exception("Gemini generate_widget_content failed")
            return {"error": "Content generation failed"}


# Module-level singleton
_gemini_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    """Return the shared GeminiClient singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
