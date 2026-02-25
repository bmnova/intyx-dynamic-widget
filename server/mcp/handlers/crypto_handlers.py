"""Cryptocurrency tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.crypto_source import CryptoSource


async def get_crypto_price(arguments: dict[str, Any]) -> list[TextContent]:
    data = CryptoSource.fetch_price(
        coin_id=arguments["coin_id"],
        currency=arguments.get("currency", "usd"),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def get_crypto_top_coins(arguments: dict[str, Any]) -> list[TextContent]:
    data = CryptoSource.fetch_top_coins(
        limit=arguments.get("limit", 10),
        currency=arguments.get("currency", "usd"),
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def get_trending_coins(arguments: dict[str, Any]) -> list[TextContent]:
    data = CryptoSource.fetch_trending()
    return [TextContent(type="text", text=json.dumps(data))]
