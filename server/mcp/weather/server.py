"""Standalone Weather MCP server exposing OpenWeatherMap tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from server.data_sources.weather_source import WeatherSource

logger = logging.getLogger(__name__)

server = Server("intyx-weather")


# --- Tools ---


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather for a city (temperature, condition, humidity)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (e.g. Istanbul, London, Tokyo)"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                        "description": "Temperature units: metric (°C) or imperial (°F)",
                    },
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day / 3-hour weather forecast for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                    },
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="get_weather_by_coords",
            description="Get current weather by geographic coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                    },
                },
                "required": ["lat", "lon"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name == "get_current_weather":
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

        elif name == "get_weather_forecast":
            forecasts = WeatherSource.fetch_forecast(
                city=arguments["city"],
                units=arguments.get("units", "metric"),
            )
            return [TextContent(type="text", text=json.dumps({"forecasts": forecasts}))]

        elif name == "get_weather_by_coords":
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

        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    except Exception as e:
        logger.exception("Weather tool error")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# --- Resources ---


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="weather://current/Istanbul",
            name="Istanbul Weather",
            description="Current weather data for Istanbul (default city)",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri.startswith("weather://current/"):
        city = uri.replace("weather://current/", "")
        try:
            data = WeatherSource.fetch_from_openweather(city)
            return json.dumps({
                "location": data.location,
                "temperature": data.temperature,
                "condition": data.condition.value,
                "humidity": data.humidity,
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Unknown resource: {uri}"})


async def main() -> None:
    """Run the Weather MCP server via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
