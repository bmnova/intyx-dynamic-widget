"""MCP (Model Context Protocol) server — handler registry architecture.

Tools are defined once in tool_definitions.py. Handlers live in
server/mcp/handlers/<domain>_handlers.py. This file wires them together
with a global error wrapper.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Coroutine

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from server import firebase_client as fb
from server.ai.gemini_client import WIDGET_CATALOG
from server.mcp.agent import run_ask
from server.mcp.handlers import (
    ai_handlers,
    air_quality_handlers,
    crypto_handlers,
    earthquake_handlers,
    exchange_rate_handlers,
    holiday_handlers,
    ip_geo_handlers,
    news_handlers,
    prayer_times_handlers,
    sports_handlers,
    trend_handlers,
    uv_index_handlers,
    weather_handlers,
    widget_handlers,
)
from server.mcp.tool_definitions import get_mcp_tools

logger = logging.getLogger(__name__)

server = Server("intyx-dynamic-widget")

# ---------------------------------------------------------------------------
# Handler registry — maps tool name → async handler(arguments) → TextContent
# ---------------------------------------------------------------------------

HandlerFn = Callable[[dict[str, Any]], Coroutine[Any, Any, list[TextContent]]]

TOOL_HANDLERS: dict[str, HandlerFn] = {
    # Widget CRUD
    "create_widget": widget_handlers.create_widget,
    "list_widgets": widget_handlers.list_widgets,
    "update_widget": widget_handlers.update_widget,
    "delete_widget": widget_handlers.delete_widget,
    # Triggers
    "create_trigger_rule": widget_handlers.create_trigger_rule,
    "evaluate_triggers": widget_handlers.evaluate_triggers,
    # Data sources & AI
    "get_data_sources": ai_handlers.get_data_sources,
    "suggest_widgets": ai_handlers.suggest_widgets,
    "get_widget_catalog": ai_handlers.get_widget_catalog,
    # Trends
    "get_trends": trend_handlers.get_trends,
    "suggest_from_trends": trend_handlers.suggest_from_trends,
    # Weather
    "get_current_weather": weather_handlers.get_current_weather,
    "get_weather_forecast": weather_handlers.get_weather_forecast,
    "get_weather_by_coords": weather_handlers.get_weather_by_coords,
    # Holidays
    "get_today_holidays": holiday_handlers.get_today_holidays,
    "get_holidays_by_date": holiday_handlers.get_holidays_by_date,
    "get_upcoming_holidays": holiday_handlers.get_upcoming_holidays,
    "get_holidays_for_month": holiday_handlers.get_holidays_for_month,
    "suggest_widget_for_holiday": holiday_handlers.suggest_widget_for_holiday,
    # Air Quality
    "get_air_quality_by_city": air_quality_handlers.get_air_quality_by_city,
    "get_air_quality_by_coords": air_quality_handlers.get_air_quality_by_coords,
    # Earthquakes
    "get_recent_earthquakes": earthquake_handlers.get_recent_earthquakes,
    "get_earthquakes_by_area": earthquake_handlers.get_earthquakes_by_area,
    # Exchange Rates
    "get_exchange_rates": exchange_rate_handlers.get_exchange_rates,
    "convert_currency": exchange_rate_handlers.convert_currency,
    # Prayer Times
    "get_prayer_times": prayer_times_handlers.get_prayer_times,
    "get_prayer_times_by_coords": prayer_times_handlers.get_prayer_times_by_coords,
    "get_prayer_methods": prayer_times_handlers.get_prayer_methods,
    # News
    "get_news_headlines": news_handlers.get_news_headlines,
    "search_news": news_handlers.search_news,
    # UV Index
    "get_uv_index": uv_index_handlers.get_uv_index,
    # IP Geolocation
    "geolocate_ip": ip_geo_handlers.geolocate_ip,
    # Cryptocurrency
    "get_crypto_price": crypto_handlers.get_crypto_price,
    "get_crypto_top_coins": crypto_handlers.get_crypto_top_coins,
    "get_trending_coins": crypto_handlers.get_trending_coins,
    # Sports
    "get_football_fixtures": sports_handlers.get_football_fixtures,
    "get_football_standings": sports_handlers.get_football_standings,
    "list_football_competitions": sports_handlers.list_football_competitions,
}


# --- Tools ---


@server.list_tools()
async def list_tools() -> list[Tool]:
    return get_mcp_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # Special case: "ask" routes through the Gemini agentic loop
    if name == "ask":
        query = (arguments.get("query") or "").strip()
        if not query:
            return [TextContent(type="text", text="query is required for ask.")]

        async def tool_runner(n: str, a: dict[str, Any]) -> str:
            out = await call_tool(n, a)
            return out[0].text if out else ""

        result_text = await run_ask(query, tool_runner)
        return [TextContent(type="text", text=result_text)]

    # Lookup handler from registry
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    # Global error wrapper — no handler can crash the server
    try:
        return await handler(arguments)
    except Exception as e:
        logger.exception("Tool '%s' failed", name)
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# --- Resources ---


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(uri="widget://list", name="All Widgets", description="List of all widget definitions"),
        Resource(uri="widget://catalog", name="Widget Catalog", description="Available widget types and parameters"),
        Resource(uri="datasource://weather", name="Weather Data", description="Current cached weather data"),
        Resource(uri="datasource://news", name="News Data", description="Current cached news data"),
        Resource(uri="datasource://horoscope", name="Horoscope Data", description="Current cached horoscope data"),
        Resource(uri="datasource://trends", name="Trend Data", description="Current viral/trending topics from social media"),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "widget://list":
        widgets = fb.get_widgets()
        return json.dumps({"widgets": widgets}, default=str)
    elif uri == "widget://catalog":
        return json.dumps(WIDGET_CATALOG, indent=2)
    elif uri == "datasource://weather":
        data = fb.get_cached_data("weather")
        return json.dumps(data or {}, default=str)
    elif uri == "datasource://news":
        data = fb.get_cached_data("news")
        return json.dumps(data or {}, default=str)
    elif uri == "datasource://horoscope":
        data = fb.get_cached_data("horoscope")
        return json.dumps(data or {}, default=str)
    elif uri == "datasource://trends":
        data = fb.get_cached_data("trends")
        return json.dumps(data or {}, default=str)
    elif uri.startswith("widget://"):
        widget_id = uri.replace("widget://", "")
        widget = fb.get_widget(widget_id)
        return json.dumps(widget or {"error": "not found"}, default=str)
    return json.dumps({"error": f"Unknown resource: {uri}"})


async def main() -> None:
    """Run the MCP server via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
