"""News tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.news_source import NewsSource


async def get_news_headlines(arguments: dict[str, Any]) -> list[TextContent]:
    data = NewsSource.fetch_headlines(
        country=arguments.get("country"),
        category=arguments.get("category"),
        limit=arguments.get("limit", 10),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def search_news(arguments: dict[str, Any]) -> list[TextContent]:
    data = NewsSource.search_news(
        query=arguments["query"],
        limit=arguments.get("limit", 10),
    )
    return [TextContent(type="text", text=json.dumps(data))]
