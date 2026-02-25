"""Earthquake tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.earthquake_source import EarthquakeSource


async def get_recent_earthquakes(arguments: dict[str, Any]) -> list[TextContent]:
    results = EarthquakeSource.fetch_recent(
        min_magnitude=float(arguments.get("min_magnitude", 3.0)),
        hours_back=int(arguments.get("hours_back", 24)),
        limit=int(arguments.get("limit", 10)),
    )
    return [TextContent(type="text", text=json.dumps({"earthquakes": results, "count": len(results)}))]


async def get_earthquakes_by_area(arguments: dict[str, Any]) -> list[TextContent]:
    results = EarthquakeSource.fetch_by_area(
        lat=float(arguments["lat"]),
        lon=float(arguments["lon"]),
        radius_km=float(arguments.get("radius_km", 500.0)),
        min_magnitude=float(arguments.get("min_magnitude", 2.0)),
        hours_back=int(arguments.get("hours_back", 72)),
        limit=int(arguments.get("limit", 10)),
    )
    return [TextContent(type="text", text=json.dumps({"earthquakes": results, "count": len(results)}))]
