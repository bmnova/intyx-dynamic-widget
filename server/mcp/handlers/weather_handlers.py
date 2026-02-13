"""Weather tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.weather_source import WeatherSource


async def get_current_weather(arguments: dict[str, Any]) -> list[TextContent]:
    data = WeatherSource.fetch_from_openweather(
        city=arguments["city"],
        units=arguments.get("units", "metric"),
    )
    result = {
        "location": data.location,
        "temperature": data.temperature,
        "condition": data.condition.value,
        "humidity": data.humidity,
    }
    return [TextContent(type="text", text=json.dumps(result))]


async def get_weather_forecast(arguments: dict[str, Any]) -> list[TextContent]:
    forecasts = WeatherSource.fetch_forecast(
        city=arguments["city"],
        units=arguments.get("units", "metric"),
    )
    return [TextContent(type="text", text=json.dumps({"forecasts": forecasts}))]


async def get_weather_by_coords(arguments: dict[str, Any]) -> list[TextContent]:
    data = WeatherSource.fetch_by_coords(
        lat=arguments["lat"],
        lon=arguments["lon"],
        units=arguments.get("units", "metric"),
    )
    result = {
        "location": data.location,
        "temperature": data.temperature,
        "condition": data.condition.value,
        "humidity": data.humidity,
    }
    return [TextContent(type="text", text=json.dumps(result))]
