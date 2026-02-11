"""Horoscope data source connector."""

from __future__ import annotations

from typing import Any, Callable

from server.models import HoroscopeData


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
        return HoroscopeData(
            sign=sign,
            prediction="Today is full of possibilities.",
            date="",
            mood="neutral",
        )

    @staticmethod
    def from_api_response(raw: dict[str, Any]) -> HoroscopeData:
        return HoroscopeData(
            sign=raw.get("sign", ""),
            prediction=raw.get("prediction", ""),
            date=raw.get("date", ""),
            mood=raw.get("mood", ""),
        )
