"""Air quality tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.air_quality_source import AirQualitySource


async def get_air_quality_by_city(arguments: dict[str, Any]) -> list[TextContent]:
    data = AirQualitySource.fetch_by_city(city=arguments["city"])
    return [TextContent(type="text", text=json.dumps(data))]


async def get_air_quality_by_coords(arguments: dict[str, Any]) -> list[TextContent]:
    data = AirQualitySource.fetch_by_coords(
        lat=arguments["lat"],
        lon=arguments["lon"],
    )
    return [TextContent(type="text", text=json.dumps(data))]
