"""Sports tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.sports_source import SportsSource


async def get_football_fixtures(arguments: dict[str, Any]) -> list[TextContent]:
    data = SportsSource.fetch_fixtures(
        competition=arguments.get("competition", "PL"),
        days_from_today=arguments.get("days_from_today", 3),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def get_football_standings(arguments: dict[str, Any]) -> list[TextContent]:
    data = SportsSource.fetch_standings(
        competition=arguments.get("competition", "PL"),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def list_football_competitions(arguments: dict[str, Any]) -> list[TextContent]:
    data = SportsSource.list_competitions()
    return [TextContent(type="text", text=json.dumps(data))]
