"""Shared tool definitions — single source of truth for MCP tools and Gemini agent.

Every tool is defined once here. Both `server.py` (MCP list_tools / call_tool)
and `agent.py` (Gemini function declarations) consume these definitions so they
never drift out of sync.
"""

from __future__ import annotations

from typing import Any

from mcp.types import Tool


# ---------------------------------------------------------------------------
# Each entry:  (name, description, input_schema, agent_visible)
#
# agent_visible=True  → tool appears in Gemini function-calling declarations
# agent_visible=False → MCP-only tool (too low-level or write-heavy for agent)
# ---------------------------------------------------------------------------

_TOOLS: list[dict[str, Any]] = [
    # ── Widget CRUD ──────────────────────────────────────────────────────
    {
        "name": "create_widget",
        "description": "Create a new widget definition in Firestore",
        "schema": {
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
        "agent_visible": False,
    },
    {
        "name": "list_widgets",
        "description": "List all widget definitions",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": True,
    },
    {
        "name": "update_widget",
        "description": "Update an existing widget",
        "schema": {
            "type": "object",
            "properties": {
                "widget_id": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["widget_id", "data"],
        },
        "agent_visible": False,
    },
    {
        "name": "delete_widget",
        "description": "Delete a widget",
        "schema": {
            "type": "object",
            "properties": {"widget_id": {"type": "string"}},
            "required": ["widget_id"],
        },
        "agent_visible": False,
    },
    # ── Triggers ─────────────────────────────────────────────────────────
    {
        "name": "create_trigger_rule",
        "description": "Create a trigger rule that binds conditions to a widget",
        "schema": {
            "type": "object",
            "properties": {
                "widget_id": {"type": "string"},
                "conditions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of condition objects (type, params)",
                },
                "match_mode": {"type": "string", "enum": ["all", "any"], "default": "all"},
            },
            "required": ["widget_id", "conditions"],
        },
        "agent_visible": False,
    },
    {
        "name": "evaluate_triggers",
        "description": "Evaluate trigger rules against a context",
        "schema": {
            "type": "object",
            "properties": {
                "context": {"type": "object", "description": "Trigger context data"},
            },
            "required": ["context"],
        },
        "agent_visible": False,
    },
    # ── Data sources ─────────────────────────────────────────────────────
    {
        "name": "get_data_sources",
        "description": "Get current cached data from all sources (weather, news, horoscope, trends)",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": True,
    },
    # ── AI ───────────────────────────────────────────────────────────────
    {
        "name": "suggest_widgets",
        "description": "Use AI to suggest widgets for a given context (weather, developer_task, etc.)",
        "schema": {
            "type": "object",
            "properties": {
                "context": {"type": "object", "description": "User context"},
            },
            "required": ["context"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_widget_catalog",
        "description": "Get the full widget catalog with all available types and parameters",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": True,
    },
    # ── Trends ───────────────────────────────────────────────────────────
    {
        "name": "get_trends",
        "description": "Get current viral/trending topics from social media",
        "schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Filter by category (dance, music, challenge, meme, sports, etc.)"},
                "platform": {"type": "string", "description": "Filter by platform (google, twitter, tiktok, etc.)"},
                "limit": {"type": "integer", "description": "Max items (default 10)"},
            },
        },
        "agent_visible": True,
    },
    {
        "name": "suggest_from_trends",
        "description": "Suggest widgets based on current viral trends + app context",
        "schema": {
            "type": "object",
            "properties": {
                "context": {"type": "object", "description": "App context (app_type, user preferences, etc.)"},
                "trend_category": {"type": "string", "description": "Optional: filter trends by category"},
            },
            "required": ["context"],
        },
        "agent_visible": True,
    },
    # ── Weather ──────────────────────────────────────────────────────────
    {
        "name": "get_current_weather",
        "description": "Get current weather for a city (temperature, condition, humidity)",
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. Istanbul, London)"},
                "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"},
            },
            "required": ["city"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_weather_forecast",
        "description": "Get 5-day / 3-hour weather forecast for a city",
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"},
            },
            "required": ["city"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_weather_by_coords",
        "description": "Get current weather by latitude/longitude",
        "schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
                "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"},
            },
            "required": ["lat", "lon"],
        },
        "agent_visible": False,
    },
    # ── Holidays ─────────────────────────────────────────────────────────
    {
        "name": "get_today_holidays",
        "description": "Get special days / holidays for today",
        "schema": {
            "type": "object",
            "properties": {"country": {"type": "string", "description": "Country code e.g. TR"}},
        },
        "agent_visible": True,
    },
    {
        "name": "get_holidays_by_date",
        "description": "Get special days for a specific date (YYYY-MM-DD)",
        "schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "ISO date string (YYYY-MM-DD)"},
                "country": {"type": "string"},
            },
            "required": ["date"],
        },
        "agent_visible": False,
    },
    {
        "name": "get_upcoming_holidays",
        "description": "Get upcoming holidays within N days from today",
        "schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "Days to look ahead (default 30)", "default": 30},
                "country": {"type": "string"},
            },
        },
        "agent_visible": True,
    },
    {
        "name": "get_holidays_for_month",
        "description": "Get all holidays in a specific month (1-12)",
        "schema": {
            "type": "object",
            "properties": {
                "month": {"type": "integer", "description": "Month number (1-12)"},
                "country": {"type": "string"},
            },
            "required": ["month"],
        },
        "agent_visible": False,
    },
    {
        "name": "suggest_widget_for_holiday",
        "description": "Suggest a widget type and params for a given holiday name",
        "schema": {
            "type": "object",
            "properties": {"holiday_name": {"type": "string", "description": "Name of the holiday"}},
            "required": ["holiday_name"],
        },
        "agent_visible": True,
    },
    # ── Gemini agent (natural language) ──────────────────────────────────
    {
        "name": "ask",
        "description": (
            "Ask in natural language. Gemini will use weather, Firebase widgets, "
            "holidays, trends, and suggest widgets as needed."
        ),
        "schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Natural language question or request"}},
            "required": ["query"],
        },
        "agent_visible": False,  # The agent IS the ask tool — no recursion
    },
]


# ── Public helpers ───────────────────────────────────────────────────────

def get_mcp_tools() -> list[Tool]:
    """Return MCP Tool objects for server.list_tools()."""
    return [
        Tool(name=t["name"], description=t["description"], inputSchema=t["schema"])
        for t in _TOOLS
    ]


def get_gemini_declarations() -> list[dict[str, Any]]:
    """Return Gemini function-calling declarations for agent.py."""
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["schema"],
        }
        for t in _TOOLS
        if t.get("agent_visible", False)
    ]
