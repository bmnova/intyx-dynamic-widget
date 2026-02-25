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
    # ── Air Quality ──────────────────────────────────────────────────────
    {
        "name": "get_air_quality_by_city",
        "description": "Get current air quality index (AQI) and pollutant levels for a city",
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. Istanbul, London, Beijing)"},
            },
            "required": ["city"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_air_quality_by_coords",
        "description": "Get current AQI for geographic coordinates",
        "schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
            },
            "required": ["lat", "lon"],
        },
        "agent_visible": False,
    },
    # ── Earthquake ───────────────────────────────────────────────────────
    {
        "name": "get_recent_earthquakes",
        "description": "Get recent earthquakes worldwide above a minimum magnitude (USGS data)",
        "schema": {
            "type": "object",
            "properties": {
                "min_magnitude": {"type": "number", "description": "Minimum Richter magnitude (default 3.0)"},
                "hours_back": {"type": "integer", "description": "Hours to look back (default 24)"},
                "limit": {"type": "integer", "description": "Max results (default 10, max 100)"},
            },
        },
        "agent_visible": True,
    },
    {
        "name": "get_earthquakes_by_area",
        "description": "Get recent earthquakes near a specific location (lat/lon radius)",
        "schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Center latitude"},
                "lon": {"type": "number", "description": "Center longitude"},
                "radius_km": {"type": "number", "description": "Search radius in km (default 500)"},
                "min_magnitude": {"type": "number", "description": "Minimum magnitude (default 2.0)"},
                "hours_back": {"type": "integer", "description": "Hours to look back (default 72)"},
                "limit": {"type": "integer", "description": "Max results (default 10)"},
            },
            "required": ["lat", "lon"],
        },
        "agent_visible": True,
    },
    # ── Exchange Rates ───────────────────────────────────────────────────
    {
        "name": "get_exchange_rates",
        "description": "Get latest foreign exchange rates for a base currency (ECB data via Frankfurter)",
        "schema": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "Base currency code (e.g. USD, EUR, TRY) — default USD"},
                "targets": {
                    "type": "string",
                    "description": "Comma-separated target currencies (e.g. 'EUR,TRY,GBP'). Leave empty for all.",
                },
            },
        },
        "agent_visible": True,
    },
    {
        "name": "convert_currency",
        "description": "Convert an amount between two currencies",
        "schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert"},
                "from_currency": {"type": "string", "description": "Source currency code (e.g. USD)"},
                "to_currency": {"type": "string", "description": "Target currency code (e.g. TRY)"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
        "agent_visible": True,
    },
    # ── Prayer Times ─────────────────────────────────────────────────────
    {
        "name": "get_prayer_times",
        "description": "Get Islamic prayer times for a city (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha)",
        "schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. Istanbul, Ankara)"},
                "country": {"type": "string", "description": "Country code (default TR)"},
                "method": {
                    "type": "string",
                    "description": "Calculation method: diyanet, isna, mwl, makkah, karachi, egypt, gulf, kuwait, qatar, singapore, france, tehran (default diyanet)",
                },
                "date": {"type": "string", "description": "Date in DD-MM-YYYY format (default today)"},
            },
            "required": ["city"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_prayer_times_by_coords",
        "description": "Get Islamic prayer times for geographic coordinates",
        "schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
                "method": {"type": "string", "description": "Calculation method (default diyanet)"},
                "date": {"type": "string", "description": "Date in DD-MM-YYYY format (default today)"},
            },
            "required": ["lat", "lon"],
        },
        "agent_visible": False,
    },
    {
        "name": "get_prayer_methods",
        "description": "List all available Islamic prayer time calculation methods",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": False,
    },
    # ── News ─────────────────────────────────────────────────────────────
    {
        "name": "get_news_headlines",
        "description": "Get top news headlines filtered by category and/or country (NewsAPI.org)",
        "schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "News category: business, entertainment, general, health, science, sports, technology",
                },
                "country": {
                    "type": "string",
                    "description": "ISO country code (e.g. us, gb, tr, de). Defaults to configured country.",
                },
                "limit": {"type": "integer", "description": "Max articles to return (default 10, max 100)"},
            },
        },
        "agent_visible": True,
    },
    {
        "name": "search_news",
        "description": "Search news articles by keyword across all sources (NewsAPI.org)",
        "schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword or phrase"},
                "limit": {"type": "integer", "description": "Max articles to return (default 10)"},
            },
            "required": ["query"],
        },
        "agent_visible": True,
    },
    # ── UV Index ─────────────────────────────────────────────────────────
    {
        "name": "get_uv_index",
        "description": "Get current UV index and sun protection advice for geographic coordinates (currentuvindex.com, no API key required)",
        "schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
            },
            "required": ["lat", "lon"],
        },
        "agent_visible": True,
    },
    # ── IP Geolocation ───────────────────────────────────────────────────
    {
        "name": "geolocate_ip",
        "description": "Get country, city, lat/lon, and timezone for an IP address (ip-api.com, no API key required). Leave ip_address empty to geolocate the caller's IP.",
        "schema": {
            "type": "object",
            "properties": {
                "ip_address": {"type": "string", "description": "IPv4 or IPv6 address to look up. Omit to use caller's IP."},
            },
        },
        "agent_visible": True,
    },
    # ── Cryptocurrency ───────────────────────────────────────────────────
    {
        "name": "get_crypto_price",
        "description": "Get current price and 24h stats for a cryptocurrency (CoinGecko, no API key required)",
        "schema": {
            "type": "object",
            "properties": {
                "coin_id": {
                    "type": "string",
                    "description": "CoinGecko coin ID (e.g. bitcoin, ethereum, solana, cardano)",
                },
                "currency": {
                    "type": "string",
                    "description": "Quote currency code (default usd). Supports usd, eur, try, gbp, btc, etc.",
                },
            },
            "required": ["coin_id"],
        },
        "agent_visible": True,
    },
    {
        "name": "get_crypto_top_coins",
        "description": "Get top N cryptocurrencies ranked by market cap (CoinGecko)",
        "schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of coins to return (default 10, max 250)"},
                "currency": {"type": "string", "description": "Quote currency (default usd)"},
            },
        },
        "agent_visible": True,
    },
    {
        "name": "get_trending_coins",
        "description": "Get currently trending cryptocurrencies on CoinGecko (top searched in last 24h)",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": True,
    },
    # ── Sports ───────────────────────────────────────────────────────────
    {
        "name": "get_football_fixtures",
        "description": "Get upcoming football (soccer) fixtures for a competition (football-data.org). Requires FOOTBALL_DATA_API_KEY.",
        "schema": {
            "type": "object",
            "properties": {
                "competition": {
                    "type": "string",
                    "description": "Competition code: PL (Premier League), PD (La Liga), BL1 (Bundesliga), SA (Serie A), FL1 (Ligue 1), CL (Champions League)",
                },
                "days_from_today": {
                    "type": "integer",
                    "description": "How many days ahead to look for fixtures (default 3)",
                },
            },
        },
        "agent_visible": True,
    },
    {
        "name": "get_football_standings",
        "description": "Get current league standings/table for a football competition (football-data.org)",
        "schema": {
            "type": "object",
            "properties": {
                "competition": {
                    "type": "string",
                    "description": "Competition code: PL, PD, BL1, SA, FL1, CL (default PL)",
                },
            },
        },
        "agent_visible": True,
    },
    {
        "name": "list_football_competitions",
        "description": "List all supported football competition codes and their names",
        "schema": {"type": "object", "properties": {}},
        "agent_visible": False,
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
