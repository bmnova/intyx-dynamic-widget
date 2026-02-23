"""Horoscope data source connector — Gemini AI-powered predictions."""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any, Callable

from server.models import HoroscopeData

logger = logging.getLogger(__name__)

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]


class HoroscopeSource:
    """Fetches and distributes horoscope data to subscribers."""

    def __init__(self, fetch_fn: Callable[[str], HoroscopeData] | None = None):
        self._fetch_fn = fetch_fn or self._default_fetch
        self._subscribers: list[Callable[[HoroscopeData], None]] = []
        self._last_data: dict[str, HoroscopeData] = {}

    async def fetch(self, sign: str) -> HoroscopeData:
        data = self._fetch_fn(sign)
        self._last_data[sign] = data
        self._notify(data)
        return data

    async def fetch_all(self) -> list[HoroscopeData]:
        """Fetch horoscopes for all signs using Gemini batch."""
        results = self._batch_fetch()
        for data in results:
            self._last_data[data.sign] = data
            self._notify(data)
        return results

    def subscribe(self, callback: Callable[[HoroscopeData], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            self._subscribers.remove(callback)

        return unsubscribe

    def get_last(self, sign: str) -> HoroscopeData | None:
        return self._last_data.get(sign)

    def _notify(self, data: HoroscopeData) -> None:
        for cb in self._subscribers:
            cb(data)

    @staticmethod
    def _default_fetch(sign: str) -> HoroscopeData:
        """Fetch a single sign's horoscope using Gemini."""
        try:
            from server.ai.gemini_client import get_gemini_client
            client = get_gemini_client()
            today = date.today().isoformat()

            response = client._model.generate_content(
                f"Write a short daily horoscope for {sign} on {today}. "
                f"Return ONLY valid JSON: "
                f'{{"prediction": "...", "mood": "positive|neutral|negative", "lucky_number": N}}'
            )
            from server.ai.gemini_client import _strip_code_fences
            text = _strip_code_fences(response.text)
            parsed = json.loads(text)

            return HoroscopeData(
                sign=sign,
                prediction=parsed.get("prediction", "Today is full of possibilities."),
                date=today,
                mood=parsed.get("mood", "neutral"),
            )
        except Exception:
            logger.exception("Horoscope fetch failed for %s", sign)
            return HoroscopeData(
                sign=sign,
                prediction="Today is full of possibilities.",
                date=date.today().isoformat(),
                mood="neutral",
            )

    @staticmethod
    def _batch_fetch() -> list[HoroscopeData]:
        """Fetch all 12 signs in a single Gemini call."""
        try:
            from server.ai.gemini_client import get_gemini_client, _strip_code_fences
            client = get_gemini_client()
            today = date.today().isoformat()

            prompt = (
                f"Write short daily horoscopes for all 12 zodiac signs for {today}. "
                f"Return ONLY valid JSON array: "
                f'[{{"sign": "aries", "prediction": "...", "mood": "positive|neutral|negative", "lucky_number": N}}, ...]'
            )
            response = client._model.generate_content(prompt)
            text = _strip_code_fences(response.text)
            parsed = json.loads(text)

            results = []
            for item in parsed:
                results.append(HoroscopeData(
                    sign=item.get("sign", ""),
                    prediction=item.get("prediction", "Today is full of possibilities."),
                    date=today,
                    mood=item.get("mood", "neutral"),
                ))
            return results
        except Exception:
            logger.exception("Batch horoscope fetch failed")
            return [
                HoroscopeData(sign=s, prediction="Today is full of possibilities.", date=date.today().isoformat(), mood="neutral")
                for s in SIGNS
            ]

    @staticmethod
    def from_api_response(raw: dict[str, Any]) -> HoroscopeData:
        return HoroscopeData(
            sign=raw.get("sign", ""),
            prediction=raw.get("prediction", ""),
            date=raw.get("date", ""),
            mood=raw.get("mood", ""),
        )
