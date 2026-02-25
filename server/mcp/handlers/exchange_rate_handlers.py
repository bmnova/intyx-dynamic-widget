"""Exchange rate tool handlers."""

from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent

from server.data_sources.exchange_rate_source import ExchangeRateSource


async def get_exchange_rates(arguments: dict[str, Any]) -> list[TextContent]:
    targets_raw = arguments.get("targets")
    targets = [t.strip() for t in targets_raw.split(",")] if isinstance(targets_raw, str) else targets_raw
    data = ExchangeRateSource.fetch_rates(
        base=arguments.get("base", "USD"),
        targets=targets or None,
    )
    return [TextContent(type="text", text=json.dumps(data))]


async def convert_currency(arguments: dict[str, Any]) -> list[TextContent]:
    data = ExchangeRateSource.convert(
        amount=float(arguments["amount"]),
        from_currency=arguments["from_currency"],
        to_currency=arguments["to_currency"],
    )
    return [TextContent(type="text", text=json.dumps(data))]
