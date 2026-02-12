"""Gemini-backed agent that orchestrates MCP tools (weather, Firebase, holidays, etc.)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine

import requests

from server.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_TURNS = 10

# Tool declarations for Gemini function calling
GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "get_current_weather",
        "description": "Get current weather for a city (temperature, condition, humidity).",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name (e.g. Istanbul, London)"},
                "units": {"type": "string", "enum": ["metric", "imperial"]},
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_weather_forecast",
        "description": "Get 5-day weather forecast for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}, "units": {"type": "string", "enum": ["metric", "imperial"]}},
            "required": ["city"],
        },
    },
    {
        "name": "list_widgets",
        "description": "List all widget definitions in Firebase.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_widget_catalog",
        "description": "Get the full widget catalog (all available widget types and parameters).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_today_holidays",
        "description": "Get special days / holidays for today. Optional country code (e.g. TR).",
        "parameters": {"type": "object", "properties": {"country": {"type": "string"}}},
    },
    {
        "name": "get_upcoming_holidays",
        "description": "Get upcoming holidays in the next N days (default 30).",
        "parameters": {
            "type": "object",
            "properties": {"days_ahead": {"type": "integer"}, "country": {"type": "string"}},
        },
    },
    {
        "name": "get_data_sources",
        "description": "Get current cached data from all sources (weather, news, horoscope, trends).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "suggest_widgets",
        "description": "Use AI to suggest widgets for a given context (e.g. weather, developer_task).",
        "parameters": {
            "type": "object",
            "properties": {"context": {"type": "object", "description": "Context for widget suggestion"}},
            "required": ["context"],
        },
    },
]


def _parse_tool_result(text: str) -> Any:
    try:
        return json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return {"raw": text}


async def run_ask(
    query: str,
    tool_runner: Callable[[str, dict[str, Any]], Coroutine[Any, Any, str]],
) -> str:
    """
    Run Gemini with function calling. tool_runner(name, args) is async and returns
    the tool result text (e.g. from MCP call_tool). Returns final model response.
    """
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set; cannot run ask agent."

    url = f"{GEMINI_API_URL}/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    contents = [{"role": "user", "parts": [{"text": query}]}]
    body = {
        "contents": contents,
        "tools": [{"function_declarations": GEMINI_FUNCTION_DECLARATIONS}],
        "tool_config": {"function_calling_config": {"mode": "AUTO", "allowed_function_names": []}},
    }

    for _ in range(MAX_TURNS):
        def _post():
            return requests.post(url, json=body, timeout=60)

        try:
            resp = await asyncio.to_thread(_post)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.exception("Gemini API request failed")
            return f"Agent error: {e!s}"

        candidates = data.get("candidates", [])
        if not candidates:
            return data.get("promptFeedback", {}).get("blockReasonMessage", "No response from model.") or "No response."

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        function_call = None
        text_parts = []

        for part in parts:
            if "functionCall" in part:
                fc = part["functionCall"]
                function_call = {"name": fc.get("name"), "args": fc.get("args") or {}}
                break
            if "text" in part:
                text_parts.append(part["text"])

        if text_parts and not function_call:
            return "\n".join(text_parts)

        if not function_call:
            return "\n".join(text_parts) if text_parts else "No response from model."

        name = function_call["name"]
        args = function_call["args"]
        logger.info("Agent calling tool: %s %s", name, args)

        try:
            result_text = await tool_runner(name, args)
        except Exception as e:
            logger.exception("Tool %s failed", name)
            result_text = json.dumps({"error": str(e)})

        result_parsed = _parse_tool_result(result_text)

        # Append model turn and function response
        contents.append({"role": "model", "parts": parts})
        contents.append({
            "role": "user",
            "parts": [{"functionResponse": {"name": name, "response": {"result": result_parsed}}}],
        })
        body["contents"] = contents

    return "Agent reached max turns without final answer."
