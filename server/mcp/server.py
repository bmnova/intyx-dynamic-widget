"""MCP (Model Context Protocol) server — Firebase, Weather, Holidays, Gemini agent."""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from server import firebase_client as fb
from server.ai.gemini_client import GeminiClient, WIDGET_CATALOG
from server.data_sources.weather_source import WeatherSource
from server.mcp.agent import run_ask
from server.mcp.holidays.data import ALL_HOLIDAYS, SpecialDay
from server.models import ColorPalette

logger = logging.getLogger(__name__)

server = Server("intyx-dynamic-widget")


def _holiday_match_date(day: SpecialDay, target: date) -> bool:
    return day.date[0] == target.month and day.date[1] == target.day


def _holiday_days_until(day: SpecialDay, from_date: date) -> int:
    target = date(from_date.year, day.date[0], day.date[1])
    if target < from_date:
        target = date(from_date.year + 1, day.date[0], day.date[1])
    return (target - from_date).days


# --- Tools ---


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_widget",
            description="Create a new widget definition in Firestore",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Widget type from catalog"},
                    "params": {"type": "object", "description": "Widget parameters"},
                    "common": {"type": "object", "description": "Common params (priority, ttl, layout, etc.)"},
                    "color_palette": {
                        "type": "object",
                        "description": "Host app color palette (primary, secondary, background, surface, etc.)",
                    },
                },
                "required": ["type", "params"],
            },
        ),
        Tool(
            name="list_widgets",
            description="List all widget definitions",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="update_widget",
            description="Update an existing widget",
            inputSchema={
                "type": "object",
                "properties": {
                    "widget_id": {"type": "string"},
                    "data": {"type": "object"},
                },
                "required": ["widget_id", "data"],
            },
        ),
        Tool(
            name="delete_widget",
            description="Delete a widget",
            inputSchema={
                "type": "object",
                "properties": {
                    "widget_id": {"type": "string"},
                },
                "required": ["widget_id"],
            },
        ),
        Tool(
            name="create_trigger_rule",
            description="Create a trigger rule that binds conditions to a widget",
            inputSchema={
                "type": "object",
                "properties": {
                    "widget_id": {"type": "string"},
                    "conditions": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of condition objects (type, params)",
                    },
                    "match_mode": {
                        "type": "string",
                        "enum": ["all", "any"],
                        "default": "all",
                    },
                },
                "required": ["widget_id", "conditions"],
            },
        ),
        Tool(
            name="evaluate_triggers",
            description="Evaluate trigger rules against a context",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "object", "description": "Trigger context data"},
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="get_data_sources",
            description="Get current cached data from all sources",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="suggest_widgets",
            description="Use AI to suggest widgets for a given context",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "object", "description": "User context"},
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="get_widget_catalog",
            description="Get the full widget catalog with all available types and parameters",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_trends",
            description="Get current viral/trending topics from social media",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (dance, music, challenge, meme, sports, etc.)"},
                    "platform": {"type": "string", "description": "Filter by platform (google, twitter, tiktok, etc.)"},
                    "limit": {"type": "integer", "description": "Max items (default 10)"},
                },
            },
        ),
        Tool(
            name="suggest_from_trends",
            description="Suggest widgets based on current viral trends + app context",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "object", "description": "App context (app_type, user preferences, etc.)"},
                    "trend_category": {"type": "string", "description": "Optional: filter trends by category"},
                },
                "required": ["context"],
            },
        ),
        # Weather
        Tool(
            name="get_current_weather",
            description="Get current weather for a city (temperature, condition, humidity)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (e.g. Istanbul, London)"},
                    "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"},
                },
                "required": ["city"],
            },
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day / 3-hour weather forecast for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}, "units": {"type": "string", "enum": ["metric", "imperial"]}},
                "required": ["city"],
            },
        ),
        Tool(
            name="get_weather_by_coords",
            description="Get current weather by latitude/longitude",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number"}, "lon": {"type": "number"},
                    "units": {"type": "string", "enum": ["metric", "imperial"]},
                },
                "required": ["lat", "lon"],
            },
        ),
        # Holidays
        Tool(
            name="get_today_holidays",
            description="Get special days / holidays for today",
            inputSchema={"type": "object", "properties": {"country": {"type": "string"}}},
        ),
        Tool(
            name="get_holidays_by_date",
            description="Get special days for a specific date (YYYY-MM-DD)",
            inputSchema={
                "type": "object",
                "properties": {"date": {"type": "string"}, "country": {"type": "string"}},
                "required": ["date"],
            },
        ),
        Tool(
            name="get_upcoming_holidays",
            description="Get upcoming holidays within N days from today",
            inputSchema={
                "type": "object",
                "properties": {"days_ahead": {"type": "integer", "default": 30}, "country": {"type": "string"}},
            },
        ),
        Tool(
            name="get_holidays_for_month",
            description="Get all holidays in a specific month (1-12)",
            inputSchema={
                "type": "object",
                "properties": {"month": {"type": "integer"}, "country": {"type": "string"}},
                "required": ["month"],
            },
        ),
        Tool(
            name="suggest_widget_for_holiday",
            description="Suggest a widget type and params for a given holiday name",
            inputSchema={
                "type": "object",
                "properties": {"holiday_name": {"type": "string"}},
                "required": ["holiday_name"],
            },
        ),
        # Gemini agent: natural language over all tools
        Tool(
            name="ask",
            description="Ask in natural language. Gemini will use weather, Firebase widgets, holidays, trends, and suggest widgets as needed. Example: 'Istanbul hava nasil ve bana uygun bir widget oner' or 'Bugun ozel gun var mi?'",
            inputSchema={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Natural language question or request"}},
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "create_widget":
        payload: dict[str, Any] = {
            "type": arguments["type"],
            "params": arguments["params"],
            "common": arguments.get("common", {}),
        }
        # Merge color_palette into common params for storage
        if "color_palette" in arguments and arguments["color_palette"]:
            palette = ColorPalette.from_dict(arguments["color_palette"])
            payload["common"]["color_palette"] = palette.to_dict()
        widget_id = fb.create_widget(payload)
        return [TextContent(type="text", text=json.dumps({"id": widget_id, "status": "created"}))]

    elif name == "list_widgets":
        widgets = fb.get_widgets()
        return [TextContent(type="text", text=json.dumps({"widgets": widgets}, default=str))]

    elif name == "update_widget":
        success = fb.update_widget(arguments["widget_id"], arguments["data"])
        status = "updated" if success else "not_found"
        return [TextContent(type="text", text=json.dumps({"status": status}))]

    elif name == "delete_widget":
        success = fb.delete_widget(arguments["widget_id"])
        status = "deleted" if success else "not_found"
        return [TextContent(type="text", text=json.dumps({"status": status}))]

    elif name == "create_trigger_rule":
        rule_id = fb.create_trigger_rule({
            "widget_id": arguments["widget_id"],
            "conditions": arguments["conditions"],
            "match_mode": arguments.get("match_mode", "all"),
        })
        return [TextContent(type="text", text=json.dumps({"id": rule_id, "status": "created"}))]

    elif name == "evaluate_triggers":
        # Delegate to the shared condition builder
        from server.triggers.conditions import build_conditions
        from server.models import (
            TriggerContext, WeatherCondition, WeatherData,
            WidgetCategory, WidgetContent, WidgetDefinition,
        )
        from server.triggers.engine import TriggerEngine, WidgetTriggerRule

        ctx_data = arguments["context"]
        weather = None
        if "weather" in ctx_data:
            w = ctx_data["weather"]
            weather = WeatherData(
                location=w.get("location", ""),
                temperature=w.get("temperature", 0),
                condition=WeatherCondition(w.get("condition", "sunny")),
                humidity=w.get("humidity", 0),
            )

        ctx = TriggerContext(
            current_date=ctx_data.get("current_date", ""),
            weather=weather,
            user_actions=ctx_data.get("user_actions", []),
            dismissed_widgets=set(ctx_data.get("dismissed_widgets", [])),
            developer_params=ctx_data.get("developer_params", {}),
        )

        engine = TriggerEngine()
        rules = fb.get_trigger_rules()
        widgets_map = {w["id"]: w for w in fb.get_widgets()}

        for rule in rules:
            wid = rule.get("widget_id")
            if wid not in widgets_map:
                continue
            wd = widgets_map[wid]
            widget_def = WidgetDefinition(
                id=wid,
                name=wd.get("name", ""),
                category=WidgetCategory(wd.get("category", "informational")),
                content=WidgetContent(title=wd.get("params", {}).get("title", ""), actions=[]),
                priority=wd.get("priority", 0),
            )
            conditions = build_conditions(rule.get("conditions", []))
            if conditions:
                engine.register(WidgetTriggerRule(widget=widget_def, conditions=conditions, match_mode=rule.get("match_mode", "all")))

        matched = engine.evaluate(ctx)
        result = [widgets_map[w.id] for w in matched if w.id in widgets_map]
        return [TextContent(type="text", text=json.dumps({"widgets": result}, default=str))]

    elif name == "get_data_sources":
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

    elif name == "suggest_widgets":
        client = GeminiClient()
        result = client.suggest_widgets(arguments["context"])
        return [TextContent(type="text", text=json.dumps(result, default=str))]

    elif name == "get_widget_catalog":
        return [TextContent(type="text", text=json.dumps(WIDGET_CATALOG, indent=2))]

    elif name == "get_trends":
        cached = fb.get_cached_data("trends")
        items = cached.get("items", []) if cached else []

        category = arguments.get("category")
        platform = arguments.get("platform")
        limit = arguments.get("limit", 10)

        if category:
            items = [t for t in items if t.get("category") == category]
        if platform:
            items = [t for t in items if t.get("platform") == platform]

        items = items[:limit]
        return [TextContent(type="text", text=json.dumps({
            "items": items,
            "count": len(items),
            "updated_at": cached.get("timestamp") if cached else None,
        }, default=str))]

    elif name == "suggest_from_trends":
        cached = fb.get_cached_data("trends")
        trend_items = cached.get("items", []) if cached else []

        trend_category = arguments.get("trend_category")
        if trend_category:
            trend_items = [t for t in trend_items if t.get("category") == trend_category]
        trend_items = trend_items[:5]

        enriched_context = {
            **arguments["context"],
            "viral_trends": trend_items,
        }

        client = GeminiClient()
        result = client.suggest_widgets(enriched_context)
        return [TextContent(type="text", text=json.dumps(result, default=str))]

    # --- Weather ---
    elif name == "get_current_weather":
        try:
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
        except Exception as e:
            logger.exception("get_current_weather failed")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_weather_forecast":
        try:
            forecasts = WeatherSource.fetch_forecast(
                city=arguments["city"],
                units=arguments.get("units", "metric"),
            )
            return [TextContent(type="text", text=json.dumps({"forecasts": forecasts}))]
        except Exception as e:
            logger.exception("get_weather_forecast failed")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_weather_by_coords":
        try:
            data = WeatherSource.fetch_by_coords(
                lat=arguments["lat"], lon=arguments["lon"],
                units=arguments.get("units", "metric"),
            )
            result = {
                "location": data.location,
                "temperature": data.temperature,
                "condition": data.condition.value,
                "humidity": data.humidity,
            }
            return [TextContent(type="text", text=json.dumps(result))]
        except Exception as e:
            logger.exception("get_weather_by_coords failed")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    # --- Holidays ---
    elif name == "get_today_holidays":
        country = arguments.get("country")
        today = date.today()
        matches = [d for d in ALL_HOLIDAYS if _holiday_match_date(d, today)]
        result = _filter_holiday_country(matches, country)
        return [TextContent(type="text", text=json.dumps({"date": today.isoformat(), "holidays": result}))]

    elif name == "get_holidays_by_date":
        country = arguments.get("country")
        target = date.fromisoformat(arguments["date"])
        matches = [d for d in ALL_HOLIDAYS if _holiday_match_date(d, target)]
        result = _filter_holiday_country(matches, country)
        return [TextContent(type="text", text=json.dumps({"date": target.isoformat(), "holidays": result}))]

    elif name == "get_upcoming_holidays":
        days_ahead = arguments.get("days_ahead", 30)
        country = arguments.get("country")
        category = arguments.get("category")
        today = date.today()
        upcoming = []
        for d in ALL_HOLIDAYS:
            dist = _holiday_days_until(d, today)
            if 0 <= dist <= days_ahead:
                if category and d.category != category:
                    continue
                if country and d.country and d.country != country:
                    continue
                entry = d.to_dict()
                entry["days_until"] = dist
                upcoming.append(entry)
        upcoming.sort(key=lambda x: x["days_until"])
        return [TextContent(type="text", text=json.dumps({"from": today.isoformat(), "to": (today + timedelta(days=days_ahead)).isoformat(), "holidays": upcoming}))]

    elif name == "get_holidays_for_month":
        month = arguments["month"]
        country = arguments.get("country")
        matches = [d for d in ALL_HOLIDAYS if d.date[0] == month]
        result = _filter_holiday_country(matches, country)
        return [TextContent(type="text", text=json.dumps({"month": month, "holidays": result}))]

    elif name == "suggest_widget_for_holiday":
        holiday_name = (arguments.get("holiday_name") or "").lower()
        match = next((d for d in ALL_HOLIDAYS if d.name.lower() == holiday_name), None) or next(
            (d for d in ALL_HOLIDAYS if holiday_name in d.name.lower()), None
        )
        if not match:
            return [TextContent(type="text", text=json.dumps({"error": "Holiday not found"}))]
        if match.category == "commercial":
            suggestion = {"widget_type": "promotional", "params": {"title": f"{match.emoji} {match.name}", "description": match.description or f"{match.name} icin ozel firsatlar", "badge_text": "Ozel Gun"}}
        elif match.category == "awareness":
            suggestion = {"widget_type": "contextual", "params": {"title": match.name, "content": match.description or f"Bugun {match.name}", "icon": "info", "source": "Ozel Gunler"}}
        else:
            suggestion = {"widget_type": "banner", "params": {"text": f"{match.name} kutlu olsun!", "emoji": match.emoji, "style": "gradient"}}
        return [TextContent(type="text", text=json.dumps({"holiday": match.to_dict(), "suggestion": suggestion}))]

    # --- Gemini agent ---
    elif name == "ask":
        query = (arguments.get("query") or "").strip()
        if not query:
            return [TextContent(type="text", text="query is required for ask.")]

        async def tool_runner(n: str, a: dict[str, Any]) -> str:
            out = await call_tool(n, a)
            return out[0].text if out else ""

        result_text = await run_ask(query, tool_runner)
        return [TextContent(type="text", text=result_text)]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


def _filter_holiday_country(days: list[SpecialDay], country: str | None) -> list[dict[str, Any]]:
    if not country:
        return [d.to_dict() for d in days]
    return [d.to_dict() for d in days if not d.country or d.country == country]


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
