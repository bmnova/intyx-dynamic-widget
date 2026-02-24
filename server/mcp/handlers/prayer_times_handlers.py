"""Prayer times tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.prayer_times_source import CALCULATION_METHODS, PrayerTimesSource


async def get_prayer_times(arguments: dict[str, Any]) -> list[TextContent]:
    data = PrayerTimesSource.fetch_by_city(
        city=arguments["city"],
        country=arguments.get("country", "TR"),
        method=arguments.get("method", "diyanet"),
        date_str=arguments.get("date"),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def get_prayer_times_by_coords(arguments: dict[str, Any]) -> list[TextContent]:
    data = PrayerTimesSource.fetch_by_coords(
        lat=float(arguments["lat"]),
        lon=float(arguments["lon"]),
        method=arguments.get("method", "diyanet"),
        date_str=arguments.get("date"),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def get_prayer_methods(arguments: dict[str, Any]) -> list[TextContent]:  # noqa: ARG001
    methods = [{"id": name, "method_number": num} for name, num in CALCULATION_METHODS.items()]
    return [TextContent(type="text", text=json.dumps({"methods": methods}))]
