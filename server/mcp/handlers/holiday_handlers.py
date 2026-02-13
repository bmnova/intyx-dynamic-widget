"""Holiday / special day tool handlers."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from mcp.types import TextContent

from server.mcp.holidays.data import ALL_HOLIDAYS, SpecialDay


def _match_date(day: SpecialDay, target: date) -> bool:
    return day.date[0] == target.month and day.date[1] == target.day


def _days_until(day: SpecialDay, from_date: date) -> int:
    target = date(from_date.year, day.date[0], day.date[1])
    if target < from_date:
        target = date(from_date.year + 1, day.date[0], day.date[1])
    return (target - from_date).days


def _filter_country(days: list[SpecialDay], country: str | None) -> list[dict[str, Any]]:
    if not country:
        return [d.to_dict() for d in days]
    return [d.to_dict() for d in days if not d.country or d.country == country]


async def get_today_holidays(arguments: dict[str, Any]) -> list[TextContent]:
    country = arguments.get("country")
    today = date.today()
    matches = [d for d in ALL_HOLIDAYS if _match_date(d, today)]
    result = _filter_country(matches, country)
    return [TextContent(type="text", text=json.dumps({"date": today.isoformat(), "holidays": result}))]


async def get_holidays_by_date(arguments: dict[str, Any]) -> list[TextContent]:
    country = arguments.get("country")
    target = date.fromisoformat(arguments["date"])
    matches = [d for d in ALL_HOLIDAYS if _match_date(d, target)]
    result = _filter_country(matches, country)
    return [TextContent(type="text", text=json.dumps({"date": target.isoformat(), "holidays": result}))]


async def get_upcoming_holidays(arguments: dict[str, Any]) -> list[TextContent]:
    days_ahead = arguments.get("days_ahead", 30)
    country = arguments.get("country")
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


async def get_holidays_for_month(arguments: dict[str, Any]) -> list[TextContent]:
    month = arguments["month"]
    country = arguments.get("country")
    matches = [d for d in ALL_HOLIDAYS if d.date[0] == month]
    result = _filter_country(matches, country)
    return [TextContent(type="text", text=json.dumps({"month": month, "holidays": result}))]


async def suggest_widget_for_holiday(arguments: dict[str, Any]) -> list[TextContent]:
    holiday_name = (arguments.get("holiday_name") or "").lower()
    match = next((d for d in ALL_HOLIDAYS if d.name.lower() == holiday_name), None) or next(
        (d for d in ALL_HOLIDAYS if holiday_name in d.name.lower()), None
    )
    if not match:
        return [TextContent(type="text", text=json.dumps({"error": "Holiday not found"}))]

    if match.category == "commercial":
        suggestion = {
            "widget_type": "promotional",
            "params": {"title": f"{match.emoji} {match.name}", "description": match.description or f"{match.name} icin ozel firsatlar", "badge_text": "Ozel Gun"},
        }
    elif match.category == "awareness":
        suggestion = {
            "widget_type": "contextual",
            "params": {"title": match.name, "content": match.description or f"Bugun {match.name}", "icon": "info", "source": "Ozel Gunler"},
        }
    else:
        suggestion = {
            "widget_type": "banner",
            "params": {"text": f"{match.name} kutlu olsun!", "emoji": match.emoji, "style": "gradient"},
        }
    return [TextContent(type="text", text=json.dumps({"holiday": match.to_dict(), "suggestion": suggestion}))]
