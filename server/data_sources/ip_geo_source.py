"""IP Geolocation data source — ip-api.com (free, no API key required)."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class IPGeoSource:
    """Fetches geolocation data for an IP address using ip-api.com."""

    BASE_URL = "http://ip-api.com/json"

    @staticmethod
    def fetch(ip_address: str | None = None) -> dict[str, Any]:
        """Fetch geolocation for the given IP (or caller's IP if omitted)."""
        target = ip_address.strip() if ip_address else ""
        url = f"{IPGeoSource.BASE_URL}/{target}" if target else IPGeoSource.BASE_URL

        try:
            resp = requests.get(
                url,
                params={"fields": "status,message,country,countryCode,region,regionName,city,lat,lon,timezone,isp,query"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("IP geolocation API error for: %s", ip_address or "auto")
            raise

        if data.get("status") != "success":
            raise ValueError(f"ip-api returned failure: {data.get('message', 'unknown error')}")

        return {
            "ip": data.get("query"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "isp": data.get("isp"),
        }
