"""Widget CRUD + trigger handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server import firebase_client as fb
from server.models import (
    ColorPalette,
    TriggerContext,
    WeatherCondition,
    WeatherData,
    WidgetCategory,
    WidgetContent,
    WidgetDefinition,
)
from server.triggers.conditions import build_conditions
from server.triggers.engine import TriggerEngine, WidgetTriggerRule


async def create_widget(arguments: dict[str, Any]) -> list[TextContent]:
    payload: dict[str, Any] = {
        "type": arguments["type"],
        "params": arguments["params"],
        "common": arguments.get("common", {}),
    }
    if arguments.get("color_palette"):
        palette = ColorPalette.from_dict(arguments["color_palette"])
        payload["common"]["color_palette"] = palette.to_dict()
    widget_id = fb.create_widget(payload)
    return [TextContent(type="text", text=json.dumps({"id": widget_id, "status": "created"}))]


async def list_widgets(arguments: dict[str, Any]) -> list[TextContent]:
    widgets = fb.get_widgets()
    return [TextContent(type="text", text=json.dumps({"widgets": widgets}, default=str))]


async def update_widget(arguments: dict[str, Any]) -> list[TextContent]:
    success = fb.update_widget(arguments["widget_id"], arguments["data"])
    status = "updated" if success else "not_found"
    return [TextContent(type="text", text=json.dumps({"status": status}))]


async def delete_widget(arguments: dict[str, Any]) -> list[TextContent]:
    success = fb.delete_widget(arguments["widget_id"])
    status = "deleted" if success else "not_found"
    return [TextContent(type="text", text=json.dumps({"status": status}))]


async def create_trigger_rule(arguments: dict[str, Any]) -> list[TextContent]:
    rule_id = fb.create_trigger_rule({
        "widget_id": arguments["widget_id"],
        "conditions": arguments["conditions"],
        "match_mode": arguments.get("match_mode", "all"),
    })
    return [TextContent(type="text", text=json.dumps({"id": rule_id, "status": "created"}))]


async def evaluate_triggers(arguments: dict[str, Any]) -> list[TextContent]:
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
            engine.register(WidgetTriggerRule(
                widget=widget_def, conditions=conditions,
                match_mode=rule.get("match_mode", "all"),
            ))

    matched = engine.evaluate(ctx)
    result = [widgets_map[w.id] for w in matched if w.id in widgets_map]
    return [TextContent(type="text", text=json.dumps({"widgets": result}, default=str))]
