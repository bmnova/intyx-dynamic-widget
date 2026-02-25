"""Exchange rate data source using the Frankfurter open API (no API key required)."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

FRANKFURTER_BASE_URL = "https://api.frankfurter.app"

# Supported currencies (subset shown to the agent)
SUPPORTED_CURRENCIES = [
    "USD", "EUR", "TRY", "GBP", "JPY", "CHF", "CAD", "AUD",
    "SAR", "AED", "RUB", "CNY", "KRW", "INR", "BRL", "MXN",
]


class ExchangeRateSource:
    """Fetches foreign exchange rates from the Frankfurter API (ECB data, free, no key)."""

    @staticmethod
    def fetch_rates(base: str = "USD", targets: list[str] | None = None) -> dict[str, Any]:
        """Fetch latest exchange rates for a base currency."""
        params: dict[str, Any] = {}
        if targets:
            params["to"] = ",".join(t.upper() for t in targets)

        try:
            resp = requests.get(
                f"{FRANKFURTER_BASE_URL}/latest",
                params={"from": base.upper(), **params},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Exchange rate API error for base=%s", base)
            raise

        return {
            "base": data.get("base"),
            "date": data.get("date"),
            "rates": data.get("rates", {}),
        }

    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> dict[str, Any]:
        """Convert an amount from one currency to another."""
        try:
            resp = requests.get(
                f"{FRANKFURTER_BASE_URL}/latest",
                params={
                    "amount": amount,
                    "from": from_currency.upper(),
                    "to": to_currency.upper(),
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception(
                "Currency conversion error: %.2f %s -> %s",
                amount, from_currency, to_currency,
            )
            raise

        converted_amount = data.get("rates", {}).get(to_currency.upper())
        return {
            "amount": amount,
            "from": data.get("base"),
            "to": to_currency.upper(),
            "result": converted_amount,
            "date": data.get("date"),
        }
