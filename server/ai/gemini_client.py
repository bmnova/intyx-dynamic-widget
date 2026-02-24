"""Gemini AI client for widget suggestion and content generation."""

from __future__ import annotations

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from server.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)

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

SYSTEM_PROMPT = """Sen bir mobil uygulama widget onerme asistanisin.
Kullanicinin context'ine (hava durumu, konum, zaman, kullanici davranislari vs.) gore
hangi widget'larin gosterilmesi gerektigine karar verirsin.

Mevcut widget katalogu:
{catalog}

ONEMLI: Eger context icinde "developer_task" alani varsa, bu developerin
sana verdigi gorev tanimidir. Ornegin:
  - "Benim appim bir kiyafet uygulamasi, kullaniciya hava durumuna gore oneri kombinler goster"
  - "Benim appim bir diyet uygulamasi, kullaniciya mevsime gore meyveler oneren widget goster"
Bu goreve gore en uygun widget tipini sec ve parametreleri doldur.
Developer'in amacina uygun, yaratici ve faydali icerikler olustur.

VIRAL TRENDLER: Eger context icinde "viral_trends" alani varsa, bu o an
sosyal medyada trend olan iceriklerdir. Her trend soyle gorunur:
  {{ "title": "...", "platform": "tiktok|twitter|google|...", "category": "dance|music|challenge|...",
     "description": "...", "image_url": "...", "engagement": 500000 }}

Bu trendleri kullanarak:
  - Uygulamanin amacina uygun trendleri sec (ornegin video app icin dans trendleri)
  - hero_image veya promotional widget tipleriyle dikkat cekici kartlar olustur
  - Trend basligini ve gorselin URL'sini widget params'ina koy
  - Aksiyon butonlari ekle (ornegin "Simdi Olustur", "Trendi Dene", "Videoyu Cek")
  - button_action'a uygulamanin deep link'ini koy (ornegin "app://generate?trend=<trend_title>")
  - Yuksek engagement'li trendlere yuksek priority ver

Eger context icinde color_palette varsa, widget'larin common alanina aynen ekle.
Bu sayede widget'lar host uygulamanin renk temasina uyumlu gorunur.

Yanit olarak SADECE gecerli JSON dondur, baska bir sey yazma.
JSON formati:
{{
  "widgets": [
    {{
      "id": "w_<unique>",
      "type": "<widget_type>",
      "params": {{ ... }},
      "common": {{
        "dismissible": true,
        "priority": 10,
        "ttl_seconds": 3600,
        "color_palette": {{ ... }}
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
        """Suggest widgets based on user context."""
        system = SYSTEM_PROMPT.format(catalog=json.dumps(WIDGET_CATALOG, indent=2))
        prompt = f"Kullanici context'i:\n{json.dumps(context, indent=2, ensure_ascii=False)}\n\nBu context'e uygun widget'lari oner."

        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=system),
            )
            text = _strip_code_fences(response.text)
            return json.loads(text)
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
