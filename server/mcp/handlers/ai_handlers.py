"""AI / data source tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server import firebase_client as fb
from server.ai.gemini_client import WIDGET_CATALOG, get_gemini_client


async def get_data_sources(arguments: dict[str, Any]) -> list[TextContent]:
    weather = fb.get_cached_data("weather")
    news = fb.get_cached_data("news")
    horoscope = fb.get_cached_data("horoscope")
    trends = fb.get_cached_data("trends")
    return [TextContent(type="text", text=json.dumps({
        "weather": weather,
        "news": news,
        "horoscope": horoscope,
        "trends": trends,
    }, default=str))]


async def suggest_widgets(arguments: dict[str, Any]) -> list[TextContent]:
    client = get_gemini_client()
    result = client.suggest_widgets(arguments["context"])
    return [TextContent(type="text", text=json.dumps(result, default=str))]


async def get_widget_catalog(arguments: dict[str, Any]) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(WIDGET_CATALOG, indent=2))]
