"""Air quality data source connector using the WAQI (World Air Quality Index) API."""

from __future__ import annotations

import logging
from typing import Any

import requests

from server.config import WAQI_API_TOKEN

logger = logging.getLogger(__name__)

# AQI level descriptors
_AQI_LEVELS = [
    (0, 50, "Good", "Air quality is satisfactory; little or no risk."),
    (51, 100, "Moderate", "Acceptable quality; some risk for sensitive individuals."),
    (101, 150, "Unhealthy for Sensitive Groups", "Sensitive groups may be affected."),
    (151, 200, "Unhealthy", "Everyone may begin to experience health effects."),
    (201, 300, "Very Unhealthy", "Health alert; emergency conditions likely."),
    (301, 500, "Hazardous", "Health warning of emergency conditions."),
]


def _aqi_level(aqi: int) -> dict[str, str]:
    for lo, hi, label, description in _AQI_LEVELS:
        if lo <= aqi <= hi:
            return {"label": label, "description": description}
    return {"label": "Hazardous", "description": "Extreme health warning."}


def _token() -> str:
    return WAQI_API_TOKEN or "demo"


class AirQualitySource:
    """Fetches real-time air quality data from the WAQI API."""

    BASE_URL = "https://api.waqi.info/feed"

    @staticmethod
    def fetch_by_city(city: str) -> dict[str, Any]:
        """Fetch current AQI data for a city name."""
        try:
            resp = requests.get(
                f"{AirQualitySource.BASE_URL}/{city}/",
                params={"token": _token()},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Air quality API error for city: %s", city)
            raise

        if data.get("status") != "ok":
            raise ValueError(f"WAQI API returned non-ok status: {data.get('status')} — {data.get('data')}")

        return AirQualitySource._parse(data["data"])

    @staticmethod
    def fetch_by_coords(lat: float, lon: float) -> dict[str, Any]:
        """Fetch current AQI data for geographic coordinates."""
        try:
            resp = requests.get(
                f"{AirQualitySource.BASE_URL}/geo:{lat};{lon}/",
                params={"token": _token()},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Air quality API error for coords (%.4f, %.4f)", lat, lon)
            raise

        if data.get("status") != "ok":
            raise ValueError(f"WAQI API returned non-ok status: {data.get('status')}")

        return AirQualitySource._parse(data["data"])

    @staticmethod
    def _parse(data: dict[str, Any]) -> dict[str, Any]:
        aqi_raw = data.get("aqi")
        try:
            aqi = int(aqi_raw) if aqi_raw is not None else 0
        except (ValueError, TypeError):
            aqi = 0

        iaqi = data.get("iaqi", {})
        city_info = data.get("city", {})

        return {
            "station": city_info.get("name", "Unknown"),
            "aqi": aqi,
            "level": _aqi_level(aqi),
            "dominant_pollutant": data.get("dominentpol", "pm25"),
            "pollutants": {
                "pm25": iaqi.get("pm25", {}).get("v"),
                "pm10": iaqi.get("pm10", {}).get("v"),
                "o3": iaqi.get("o3", {}).get("v"),
                "no2": iaqi.get("no2", {}).get("v"),
                "so2": iaqi.get("so2", {}).get("v"),
                "co": iaqi.get("co", {}).get("v"),
            },
            "time": data.get("time", {}).get("s"),
        }
