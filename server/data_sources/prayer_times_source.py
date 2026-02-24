"""Prayer times data source using the Aladhan API (free, no API key required)."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import requests

logger = logging.getLogger(__name__)

ALADHAN_BASE_URL = "https://api.aladhan.com/v1"

# Calculation methods
CALCULATION_METHODS: dict[str, int] = {
    "diyanet": 13,        # Turkey Diyanet
    "isna": 2,            # Islamic Society of North America
    "mwl": 3,             # Muslim World League
    "makkah": 4,          # Umm Al-Qura, Makkah
    "karachi": 1,         # University of Islamic Sciences, Karachi
    "egypt": 5,           # Egyptian General Authority of Survey
    "tehran": 7,          # Institute of Geophysics, University of Tehran
    "gulf": 8,            # Gulf Region
    "kuwait": 9,          # Kuwait
    "qatar": 10,          # Qatar
    "singapore": 11,      # Majlis Ugama Islam Singapura
    "france": 12,         # Union Organisation Islamique de France
}

PRAYER_NAMES = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha", "Midnight"]


class PrayerTimesSource:
    """Fetches Islamic prayer times from the Aladhan API."""

    @staticmethod
    def fetch_by_city(
        city: str,
        country: str = "TR",
        method: str = "diyanet",
        date_str: str | None = None,
    ) -> dict[str, Any]:
        """Fetch prayer times for a city on a given date (defaults to today)."""
        date_param = date_str or date.today().strftime("%d-%m-%Y")
        method_id = CALCULATION_METHODS.get(method.lower(), 13)

        try:
            resp = requests.get(
                f"{ALADHAN_BASE_URL}/timingsByCity/{date_param}",
                params={"city": city, "country": country, "method": method_id},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Prayer times API error for city=%s country=%s", city, country)
            raise

        if data.get("code") != 200:
            raise ValueError(f"Aladhan API error: {data.get('status')}")

        return PrayerTimesSource._parse(data["data"])

    @staticmethod
    def fetch_by_coords(
        lat: float,
        lon: float,
        method: str = "diyanet",
        date_str: str | None = None,
    ) -> dict[str, Any]:
        """Fetch prayer times for geographic coordinates on a given date."""
        date_param = date_str or date.today().strftime("%d-%m-%Y")
        method_id = CALCULATION_METHODS.get(method.lower(), 13)

        try:
            resp = requests.get(
                f"{ALADHAN_BASE_URL}/timings/{date_param}",
                params={"latitude": lat, "longitude": lon, "method": method_id},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Prayer times API error for coords (%.4f, %.4f)", lat, lon)
            raise

        if data.get("code") != 200:
            raise ValueError(f"Aladhan API error: {data.get('status')}")

        return PrayerTimesSource._parse(data["data"])

    @staticmethod
    def _parse(data: dict[str, Any]) -> dict[str, Any]:
        timings = data.get("timings", {})
        date_info = data.get("date", {})
        meta = data.get("meta", {})

        return {
            "date": date_info.get("readable"),
            "hijri_date": date_info.get("hijri", {}).get("date"),
            "timezone": meta.get("timezone"),
            "method": meta.get("method", {}).get("name"),
            "times": {
                "fajr": timings.get("Fajr"),
                "sunrise": timings.get("Sunrise"),
                "dhuhr": timings.get("Dhuhr"),
                "asr": timings.get("Asr"),
                "maghrib": timings.get("Maghrib"),
                "isha": timings.get("Isha"),
                "midnight": timings.get("Midnight"),
            },
        }
