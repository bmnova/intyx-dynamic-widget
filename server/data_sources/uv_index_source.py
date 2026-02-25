"""UV Index data source — currentuvindex.com (free, no API key required)."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

_UV_RISK_LEVELS = [
    (0, 2, "Low", "No protection needed for most people."),
    (3, 5, "Moderate", "Seek shade during midday hours."),
    (6, 7, "High", "Wear sunscreen SPF 30+ and protective clothing."),
    (8, 10, "Very High", "Take extra precautions — unprotected skin can burn quickly."),
    (11, 99, "Extreme", "Avoid sun exposure; unprotected skin can burn in minutes."),
]


def _uv_risk(uv: float) -> dict[str, str]:
    idx = int(uv)
    for lo, hi, label, advice in _UV_RISK_LEVELS:
        if lo <= idx <= hi:
            return {"label": label, "advice": advice}
    return {"label": "Extreme", "advice": "Avoid sun exposure."}


class UVIndexSource:
    """Fetches real-time UV index data from currentuvindex.com."""

    BASE_URL = "https://currentuvindex.com/api/v1/uvi"

    @staticmethod
    def fetch_by_coords(lat: float, lon: float) -> dict[str, Any]:
        """Fetch current UV index for geographic coordinates."""
        try:
            resp = requests.get(
                UVIndexSource.BASE_URL,
                params={"latitude": lat, "longitude": lon},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("UV index API error for coords (%.4f, %.4f)", lat, lon)
            raise

        now = data.get("now", {})
        uv = now.get("uvi", 0.0)

        return {
            "latitude": lat,
            "longitude": lon,
            "uv_index": round(uv, 1),
            "risk": _uv_risk(uv),
            "timestamp": now.get("time"),
        }
