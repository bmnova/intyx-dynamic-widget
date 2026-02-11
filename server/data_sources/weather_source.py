"""Weather data source connector."""

from __future__ import annotations

from typing import Any, Callable

from server.models import WeatherCondition, WeatherData


class WeatherSource:
    """Fetches and distributes weather data to subscribers."""

    def __init__(self, fetch_fn: Callable[[], WeatherData] | None = None):
        self._fetch_fn = fetch_fn or self._default_fetch
        self._subscribers: list[Callable[[WeatherData], None]] = []
        self._last_data: WeatherData | None = None

    async def fetch(self) -> WeatherData:
        data = self._fetch_fn()
        self._last_data = data
        self._notify(data)
        return data

    def subscribe(self, callback: Callable[[WeatherData], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            self._subscribers.remove(callback)

        return unsubscribe

    @property
    def last_data(self) -> WeatherData | None:
        return self._last_data

    def _notify(self, data: WeatherData) -> None:
        for cb in self._subscribers:
            cb(data)

    @staticmethod
    def _default_fetch() -> WeatherData:
        """Default placeholder fetch — replace with real API integration."""
        return WeatherData(
            location="Istanbul",
            temperature=15.0,
            condition=WeatherCondition.CLOUDY,
            humidity=65.0,
        )

    @staticmethod
    def from_api_response(raw: dict[str, Any]) -> WeatherData:
        """Parse a raw API response dict into a WeatherData instance."""
        return WeatherData(
            location=raw.get("location", ""),
            temperature=float(raw.get("temperature", 0)),
            condition=WeatherCondition(raw.get("condition", "sunny")),
            humidity=float(raw.get("humidity", 0)),
        )
