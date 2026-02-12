"""Periodic data source polling scheduler with exponential backoff."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from server.config import (
    HOROSCOPE_POLL_INTERVAL,
    NEWS_POLL_INTERVAL,
    WEATHER_POLL_INTERVAL,
)
from server.data_sources.horoscope_source import HoroscopeSource
from server.data_sources.news_source import NewsSource
from server.data_sources.weather_source import WeatherSource
from server import firebase_client as fb

logger = logging.getLogger(__name__)

# Backoff config
_MAX_BACKOFF = 300  # 5 minutes cap
_INITIAL_BACKOFF = 2


class DataScheduler:
    """Manages periodic polling of all data sources."""

    def __init__(self) -> None:
        self.weather_source = WeatherSource()
        self.news_source = NewsSource()
        self.horoscope_source = HoroscopeSource()
        self._running = False

    async def start(self) -> None:
        """Start all polling tasks."""
        self._running = True
        logger.info("DataScheduler started")
        await asyncio.gather(
            self._poll_weather(),
            self._poll_news(),
            self._poll_horoscope(),
        )

    def stop(self) -> None:
        """Stop polling."""
        self._running = False
        logger.info("DataScheduler stopped")

    async def _poll_weather(self) -> None:
        consecutive_failures = 0
        while self._running:
            try:
                data = await self.weather_source.fetch()
                fb.cache_data("weather", {
                    "location": data.location,
                    "temperature": data.temperature,
                    "condition": data.condition.value,
                    "humidity": data.humidity,
                    "timestamp": data.timestamp,
                })
                logger.info("Weather data updated: %s %.1f°C", data.location, data.temperature)
                consecutive_failures = 0
            except Exception:
                consecutive_failures += 1
                backoff = min(_INITIAL_BACKOFF ** consecutive_failures, _MAX_BACKOFF)
                logger.exception("Weather poll failed (attempt %d, backoff %ds)", consecutive_failures, backoff)
                await asyncio.sleep(backoff)
                continue
            await asyncio.sleep(WEATHER_POLL_INTERVAL)

    async def _poll_news(self) -> None:
        consecutive_failures = 0
        while self._running:
            try:
                data = await self.news_source.fetch()
                fb.cache_data("news", {
                    "items": [
                        {
                            "headline": n.headline,
                            "category": n.category,
                            "source": n.source,
                            "url": n.url,
                        }
                        for n in data
                    ],
                    "timestamp": time.time(),
                })
                logger.info("News data updated: %d items", len(data))
                consecutive_failures = 0
            except Exception:
                consecutive_failures += 1
                backoff = min(_INITIAL_BACKOFF ** consecutive_failures, _MAX_BACKOFF)
                logger.exception("News poll failed (attempt %d, backoff %ds)", consecutive_failures, backoff)
                await asyncio.sleep(backoff)
                continue
            await asyncio.sleep(NEWS_POLL_INTERVAL)

    async def _poll_horoscope(self) -> None:
        signs = [
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
        ]
        consecutive_failures = 0
        while self._running:
            try:
                results: dict[str, Any] = {}
                for sign in signs:
                    data = await self.horoscope_source.fetch(sign)
                    results[sign] = {
                        "sign": data.sign,
                        "prediction": data.prediction,
                        "date": data.date,
                        "mood": data.mood,
                    }
                fb.cache_data("horoscope", {"signs": results, "timestamp": time.time()})
                logger.info("Horoscope data updated: %d signs", len(results))
                consecutive_failures = 0
            except Exception:
                consecutive_failures += 1
                backoff = min(_INITIAL_BACKOFF ** consecutive_failures, _MAX_BACKOFF)
                logger.exception("Horoscope poll failed (attempt %d, backoff %ds)", consecutive_failures, backoff)
                await asyncio.sleep(backoff)
                continue
            await asyncio.sleep(HOROSCOPE_POLL_INTERVAL)
