"""Special Days / Holidays MCP server.

Provides tools to query upcoming holidays, today's special days,
and holidays by date range. Useful for triggering seasonal widgets.
"""

from __future__ import annotations

import json
import logging
from datetime import date, timedelta
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

from server.mcp.holidays.data import ALL_HOLIDAYS, SpecialDay

logger = logging.getLogger(__name__)

server = Server("intyx-holidays")


def _match_date(day: SpecialDay, target: date) -> bool:
    return day.date[0] == target.month and day.date[1] == target.day


def _days_until(day: SpecialDay, from_date: date) -> int:
    target = date(from_date.year, day.date[0], day.date[1])
    if target < from_date:
        target = date(from_date.year + 1, day.date[0], day.date[1])
    return (target - from_date).days


# --- Tools ---


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_today_holidays",
            description="Get special days / holidays for today",
            inputSchema={
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "Filter by country code (e.g. TR). Omit for all.",
                    },
                },
            },
        ),
        Tool(
            name="get_holidays_by_date",
            description="Get special days for a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "ISO date string (YYYY-MM-DD)",
                    },
                    "country": {"type": "string"},
                },
                "required": ["date"],
            },
        ),
        Tool(
            name="get_upcoming_holidays",
            description="Get upcoming holidays within N days from today",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead (default: 30)",
                        "default": 30,
                    },
                    "country": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["religious", "national", "international", "commercial", "awareness"],
                    },
                },
            },
        ),
        Tool(
            name="get_holidays_for_month",
            description="Get all holidays in a specific month",
            inputSchema={
                "type": "object",
                "properties": {
                    "month": {"type": "integer", "description": "Month number (1-12)"},
                    "country": {"type": "string"},
                },
                "required": ["month"],
            },
        ),
        Tool(
            name="suggest_widget_for_holiday",
            description="Suggest a widget type and params for a given holiday/special day",
            inputSchema={
                "type": "object",
                "properties": {
                    "holiday_name": {"type": "string", "description": "Name of the holiday"},
                },
                "required": ["holiday_name"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    country = arguments.get("country")

    def filter_country(days: list[SpecialDay]) -> list[dict]:
        result = []
        for d in days:
            if country and d.country and d.country != country:
                continue
            result.append(d.to_dict())
        return result

    if name == "get_today_holidays":
        today = date.today()
        matches = [d for d in ALL_HOLIDAYS if _match_date(d, today)]
        return [TextContent(type="text", text=json.dumps({
            "date": today.isoformat(),
            "holidays": filter_country(matches),
        }))]

    elif name == "get_holidays_by_date":
        target = date.fromisoformat(arguments["date"])
        matches = [d for d in ALL_HOLIDAYS if _match_date(d, target)]
        return [TextContent(type="text", text=json.dumps({
            "date": target.isoformat(),
            "holidays": filter_country(matches),
        }))]

    elif name == "get_upcoming_holidays":
        days_ahead = arguments.get("days_ahead", 30)
        category = arguments.get("category")
        today = date.today()
        upcoming = []
        for d in ALL_HOLIDAYS:
            dist = _days_until(d, today)
            if 0 <= dist <= days_ahead:
                if category and d.category != category:
                    continue
                if country and d.country and d.country != country:
                    continue
                entry = d.to_dict()
                entry["days_until"] = dist
                upcoming.append(entry)
        upcoming.sort(key=lambda x: x["days_until"])
        return [TextContent(type="text", text=json.dumps({
            "from": today.isoformat(),
            "to": (today + timedelta(days=days_ahead)).isoformat(),
            "holidays": upcoming,
        }))]

    elif name == "get_holidays_for_month":
        month = arguments["month"]
        matches = [d for d in ALL_HOLIDAYS if d.date[0] == month]
        return [TextContent(type="text", text=json.dumps({
            "month": month,
            "holidays": filter_country(matches),
        }))]

    elif name == "suggest_widget_for_holiday":
        holiday_name = arguments["holiday_name"].lower()
        match = next((d for d in ALL_HOLIDAYS if d.name.lower() == holiday_name), None)

        if not match:
            # Fuzzy match
            match = next(
                (d for d in ALL_HOLIDAYS if holiday_name in d.name.lower()),
                None,
            )

        if not match:
            return [TextContent(type="text", text=json.dumps({"error": "Holiday not found"}))]

        # Suggest widget based on category
        if match.category == "commercial":
            suggestion = {
                "widget_type": "promotional",
                "params": {
                    "title": f"{match.emoji} {match.name}",
                    "description": match.description or f"{match.name} icin ozel firsatlar",
                    "badge_text": "Ozel Gun",
                },
                "alternative_type": "banner",
                "alternative_params": {
                    "text": f"{match.name} kutlu olsun!",
                    "emoji": match.emoji,
                    "style": "gradient",
                },
            }
        elif match.category == "awareness":
            suggestion = {
                "widget_type": "contextual",
                "params": {
                    "title": match.name,
                    "content": match.description or f"Bugun {match.name}",
                    "icon": "info",
                    "source": "Ozel Gunler",
                },
                "alternative_type": "banner",
                "alternative_params": {
                    "text": f"{match.emoji} {match.name}",
                    "style": "outlined",
                },
            }
        else:
            suggestion = {
                "widget_type": "banner",
                "params": {
                    "text": f"{match.name} kutlu olsun!",
                    "emoji": match.emoji,
                    "style": "gradient",
                },
                "alternative_type": "informational",
                "alternative_params": {
                    "title": match.name,
                    "message": match.description or f"Bugun {match.name}",
                    "severity": "info",
                },
            }

        return [TextContent(type="text", text=json.dumps({
            "holiday": match.to_dict(),
            "suggestion": suggestion,
        }))]

    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# --- Resources ---


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="holidays://today",
            name="Today's Holidays",
            description="Special days and holidays for today",
        ),
        Resource(
            uri="holidays://upcoming",
            name="Upcoming Holidays",
            description="Holidays in the next 30 days",
        ),
        Resource(
            uri="holidays://all",
            name="All Holidays",
            description="Complete holiday database",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "holidays://today":
        today = date.today()
        matches = [d.to_dict() for d in ALL_HOLIDAYS if _match_date(d, today)]
        return json.dumps({"date": today.isoformat(), "holidays": matches})

    elif uri == "holidays://upcoming":
        today = date.today()
        upcoming = []
        for d in ALL_HOLIDAYS:
            dist = _days_until(d, today)
            if 0 <= dist <= 30:
                entry = d.to_dict()
                entry["days_until"] = dist
                upcoming.append(entry)
        upcoming.sort(key=lambda x: x["days_until"])
        return json.dumps({"holidays": upcoming})

    elif uri == "holidays://all":
        return json.dumps({"holidays": [d.to_dict() for d in ALL_HOLIDAYS]})

    return json.dumps({"error": f"Unknown resource: {uri}"})


async def main() -> None:
    """Run the Holidays MCP server via stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
