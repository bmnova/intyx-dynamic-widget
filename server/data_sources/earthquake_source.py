"""Earthquake data source connector using the free USGS Earthquake Hazards API."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

logger = logging.getLogger(__name__)

USGS_BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def _iso_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


class EarthquakeSource:
    """Fetches earthquake data from the USGS Earthquake Hazards API (no API key required)."""

    @staticmethod
    def fetch_recent(
        min_magnitude: float = 3.0,
        hours_back: int = 24,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch recent earthquakes worldwide above a minimum magnitude."""
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)

        params = {
            "format": "geojson",
            "starttime": _iso_date(start_time),
            "endtime": _iso_date(end_time),
            "minmagnitude": min_magnitude,
            "orderby": "time",
            "limit": min(limit, 100),
        }
        return EarthquakeSource._query(params)

    @staticmethod
    def fetch_by_area(
        lat: float,
        lon: float,
        radius_km: float = 500.0,
        min_magnitude: float = 2.0,
        hours_back: int = 72,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch earthquakes near geographic coordinates."""
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)

        params = {
            "format": "geojson",
            "starttime": _iso_date(start_time),
            "endtime": _iso_date(end_time),
            "latitude": lat,
            "longitude": lon,
            "maxradiuskm": radius_km,
            "minmagnitude": min_magnitude,
            "orderby": "time",
            "limit": min(limit, 100),
        }
        return EarthquakeSource._query(params)

    @staticmethod
    def _query(params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            resp = requests.get(USGS_BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("USGS earthquake API error")
            raise

        results: list[dict[str, Any]] = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None, None])
            results.append({
                "id": feature.get("id"),
                "magnitude": props.get("mag"),
                "place": props.get("place", "Unknown"),
                "time": datetime.fromtimestamp(
                    props["time"] / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%SZ") if props.get("time") else None,
                "depth_km": coords[2],
                "longitude": coords[0],
                "latitude": coords[1],
                "url": props.get("url"),
                "alert": props.get("alert"),
                "tsunami": bool(props.get("tsunami")),
            })
        return results
