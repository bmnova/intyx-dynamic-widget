"""Weather data source connector with OpenWeatherMap API support."""

from __future__ import annotations

import logging
from typing import Any, Callable

import requests

from server.config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
from server.models import WeatherCondition, WeatherData

logger = logging.getLogger(__name__)

# OpenWeatherMap condition code -> our enum mapping
_OWM_CONDITION_MAP = {
    "Clear": WeatherCondition.SUNNY,
    "Clouds": WeatherCondition.CLOUDY,
    "Rain": WeatherCondition.RAINY,
    "Drizzle": WeatherCondition.RAINY,
    "Snow": WeatherCondition.SNOWY,
    "Thunderstorm": WeatherCondition.STORMY,
}


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
        temperature = raw.get("temperature", 0)
        humidity = raw.get("humidity", 0)

        # Type-check: ensure numeric values
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 0.0
        if isinstance(humidity, str):
            try:
                humidity = float(humidity)
            except (ValueError, TypeError):
                humidity = 0.0

        return WeatherData(
            location=raw.get("location", ""),
            temperature=float(temperature),
            condition=WeatherCondition(raw.get("condition", "sunny")),
            humidity=float(humidity),
        )

    @staticmethod
    def fetch_from_openweather(city: str, units: str = "metric") -> WeatherData:
        """Fetch current weather from OpenWeatherMap API."""
        if not OPENWEATHER_API_KEY:
            logger.warning("OPENWEATHER_API_KEY not set, returning placeholder")
            return WeatherData(
                location=city, temperature=0.0,
                condition=WeatherCondition.CLOUDY, humidity=0.0,
            )

        try:
            resp = requests.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params={"q": city, "appid": OPENWEATHER_API_KEY, "units": units},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return WeatherSource._parse_owm_current(data)
        except requests.ConnectionError:
            logger.exception("Weather API connection error for %s", city)
            raise
        except requests.Timeout:
            logger.exception("Weather API timeout for %s", city)
            raise
        except requests.HTTPError as e:
            logger.exception("Weather API HTTP error for %s: %s", city, e.response.status_code if e.response else "unknown")
            raise

    @staticmethod
    def fetch_forecast(city: str, units: str = "metric") -> list[dict[str, Any]]:
        """Fetch 5-day/3-hour forecast from OpenWeatherMap API."""
        if not OPENWEATHER_API_KEY:
            return []

        try:
            resp = requests.get(
                f"{OPENWEATHER_BASE_URL}/forecast",
                params={"q": city, "appid": OPENWEATHER_API_KEY, "units": units},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Weather forecast API error for %s", city)
            raise

        forecasts = []
        for item in data.get("list", []):
            main_weather = item.get("weather", [{}])[0].get("main", "Clear")
            forecasts.append({
                "dt": item["dt"],
                "dt_txt": item.get("dt_txt", ""),
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "temp_min": item["main"]["temp_min"],
                "temp_max": item["main"]["temp_max"],
                "humidity": item["main"]["humidity"],
                "condition": _OWM_CONDITION_MAP.get(main_weather, WeatherCondition.CLOUDY).value,
                "description": item.get("weather", [{}])[0].get("description", ""),
                "wind_speed": item.get("wind", {}).get("speed", 0),
            })
        return forecasts

    @staticmethod
    def fetch_by_coords(lat: float, lon: float, units: str = "metric") -> WeatherData:
        """Fetch current weather by coordinates."""
        if not OPENWEATHER_API_KEY:
            return WeatherData(
                location=f"{lat},{lon}", temperature=0.0,
                condition=WeatherCondition.CLOUDY, humidity=0.0,
            )

        try:
            resp = requests.get(
                f"{OPENWEATHER_BASE_URL}/weather",
                params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": units},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return WeatherSource._parse_owm_current(data)
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Weather API error for coords (%.2f, %.2f)", lat, lon)
            raise

    @staticmethod
    def _parse_owm_current(data: dict[str, Any]) -> WeatherData:
        """Parse OpenWeatherMap current weather response."""
        main_weather = data.get("weather", [{}])[0].get("main", "Clear")
        condition = _OWM_CONDITION_MAP.get(main_weather, WeatherCondition.CLOUDY)

        return WeatherData(
            location=data.get("name", ""),
            temperature=data.get("main", {}).get("temp", 0.0),
            condition=condition,
            humidity=data.get("main", {}).get("humidity", 0.0),
        )
