"""MCP (Model Context Protocol) server implementation."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from server import firebase_client as fb
from server.ai.gemini_client import GeminiClient, WIDGET_CATALOG
from server.models import ColorPalette

logger = logging.getLogger(__name__)

server = Server("intyx-dynamic-widget")


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

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


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
