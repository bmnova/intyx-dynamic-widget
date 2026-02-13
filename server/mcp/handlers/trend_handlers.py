"""Trend / viral content tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server import firebase_client as fb
from server.ai.gemini_client import get_gemini_client


async def get_trends(arguments: dict[str, Any]) -> list[TextContent]:
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


async def suggest_from_trends(arguments: dict[str, Any]) -> list[TextContent]:
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

    client = get_gemini_client()
    result = client.suggest_widgets(enriched_context)
    return [TextContent(type="text", text=json.dumps(result, default=str))]
