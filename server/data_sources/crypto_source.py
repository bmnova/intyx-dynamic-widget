"""Cryptocurrency data source — CoinGecko API (free public endpoints, no key required)."""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

_HEADERS = {"Accept": "application/json", "User-Agent": "intyx-dynamic-widget/1.0"}


class CryptoSource:
    """Fetches cryptocurrency market data from CoinGecko."""

    @staticmethod
    def fetch_price(coin_id: str, currency: str = "usd") -> dict[str, Any]:
        """Fetch current price and market data for a single coin."""
        try:
            resp = requests.get(
                f"{COINGECKO_BASE}/coins/markets",
                params={
                    "vs_currency": currency.lower(),
                    "ids": coin_id.lower(),
                    "order": "market_cap_desc",
                    "per_page": 1,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h",
                },
                headers=_HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("CoinGecko price fetch error for: %s", coin_id)
            raise

        if not results:
            raise ValueError(f"Coin not found: {coin_id}")

        c = results[0]
        return {
            "id": c.get("id"),
            "name": c.get("name"),
            "symbol": c.get("symbol", "").upper(),
            "currency": currency.upper(),
            "price": c.get("current_price"),
            "market_cap": c.get("market_cap"),
            "volume_24h": c.get("total_volume"),
            "change_24h_pct": c.get("price_change_percentage_24h"),
            "high_24h": c.get("high_24h"),
            "low_24h": c.get("low_24h"),
            "last_updated": c.get("last_updated"),
        }

    @staticmethod
    def fetch_top_coins(limit: int = 10, currency: str = "usd") -> dict[str, Any]:
        """Fetch top N coins by market cap."""
        try:
            resp = requests.get(
                f"{COINGECKO_BASE}/coins/markets",
                params={
                    "vs_currency": currency.lower(),
                    "order": "market_cap_desc",
                    "per_page": min(limit, 250),
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h",
                },
                headers=_HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            results = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("CoinGecko top coins fetch error")
            raise

        return {
            "currency": currency.upper(),
            "coins": [
                {
                    "rank": c.get("market_cap_rank"),
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "symbol": c.get("symbol", "").upper(),
                    "price": c.get("current_price"),
                    "change_24h_pct": c.get("price_change_percentage_24h"),
                    "market_cap": c.get("market_cap"),
                }
                for c in results
            ],
        }

    @staticmethod
    def fetch_trending() -> dict[str, Any]:
        """Fetch currently trending coins on CoinGecko (top 7 searched in 24h)."""
        try:
            resp = requests.get(
                f"{COINGECKO_BASE}/search/trending",
                headers=_HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("CoinGecko trending fetch error")
            raise

        coins = data.get("coins", [])
        return {
            "trending_coins": [
                {
                    "rank": i + 1,
                    "id": item.get("item", {}).get("id"),
                    "name": item.get("item", {}).get("name"),
                    "symbol": item.get("item", {}).get("symbol"),
                    "market_cap_rank": item.get("item", {}).get("market_cap_rank"),
                }
                for i, item in enumerate(coins)
            ]
        }
