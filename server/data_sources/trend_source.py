"""Trend/viral content data source connector.

Aggregates trending topics from multiple platforms:
- Google Trends (via pytrends or RSS)
- Twitter/X (via API v2)
- Fallback: curated/placeholder trends

The AI agent uses these trends to suggest context-aware widgets.
For example, a video generation app can show "Generate this viral dance" widgets.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

import requests

from server.config import TRENDS_REGION, TWITTER_BEARER_TOKEN
from server.models import TrendItem, TrendPlatform

logger = logging.getLogger(__name__)

# Google Trends RSS feed URL
_GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo={region}"


class TrendSource:
    """Fetches and distributes trending/viral content from social media."""

    def __init__(self, fetch_fn: Callable[[], list[TrendItem]] | None = None):
        self._fetch_fn = fetch_fn or self._aggregate_fetch
        self._subscribers: list[Callable[[list[TrendItem]], None]] = []
        self._last_data: list[TrendItem] = []

    async def fetch(self) -> list[TrendItem]:
        data = self._fetch_fn()
        self._last_data = data
        self._notify(data)
        return data

    def subscribe(self, callback: Callable[[list[TrendItem]], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            self._subscribers.remove(callback)

        return unsubscribe

    @property
    def last_data(self) -> list[TrendItem]:
        return self._last_data

    def _notify(self, data: list[TrendItem]) -> None:
        for cb in self._subscribers:
            cb(data)

    def _aggregate_fetch(self) -> list[TrendItem]:
        """Fetch trends from all available sources and merge."""
        items: list[TrendItem] = []

        # Google Trends (always available, no API key needed)
        try:
            items.extend(self._fetch_google_trends())
        except Exception:
            logger.exception("Google Trends fetch failed")

        # Twitter/X (needs bearer token)
        if TWITTER_BEARER_TOKEN:
            try:
                items.extend(self._fetch_twitter_trends())
            except Exception:
                logger.exception("Twitter trends fetch failed")

        # Sort by engagement (highest first)
        items.sort(key=lambda t: t.engagement, reverse=True)
        return items[:20]  # Cap at 20 trends

    @staticmethod
    def _fetch_google_trends() -> list[TrendItem]:
        """Fetch trending topics from Google Trends RSS feed."""
        url = _GOOGLE_TRENDS_RSS.format(region=TRENDS_REGION)

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Google Trends RSS fetch failed")
            raise

        # Parse the RSS XML — simple extraction without heavy XML deps
        items: list[TrendItem] = []
        content = resp.text

        # Extract <item> blocks from RSS
        import re
        item_blocks = re.findall(r"<item>(.*?)</item>", content, re.DOTALL)

        for block in item_blocks:
            title_match = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", block)
            if not title_match:
                title_match = re.search(r"<title>(.*?)</title>", block)
            title = title_match.group(1).strip() if title_match else ""

            traffic_match = re.search(r"<ht:approx_traffic>(.*?)</ht:approx_traffic>", block)
            traffic_str = traffic_match.group(1).strip() if traffic_match else "0"
            # Parse "500,000+" -> 500000
            engagement = int(traffic_str.replace(",", "").replace("+", "") or "0")

            desc_match = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", block)
            if not desc_match:
                desc_match = re.search(r"<description>(.*?)</description>", block)
            description = desc_match.group(1).strip() if desc_match else ""

            link_match = re.search(r"<link>(.*?)</link>", block)
            url = link_match.group(1).strip() if link_match else ""

            img_match = re.search(r"<ht:picture>(.*?)</ht:picture>", block)
            image_url = img_match.group(1).strip() if img_match else ""

            if title:
                items.append(TrendItem(
                    title=title,
                    platform=TrendPlatform.GOOGLE,
                    category=_guess_category(title, description),
                    description=description,
                    image_url=image_url,
                    url=url,
                    engagement=engagement,
                    region=TRENDS_REGION,
                ))

        return items

    @staticmethod
    def _fetch_twitter_trends() -> list[TrendItem]:
        """Fetch trending topics from Twitter/X API v2."""
        # Twitter v1.1 trends/place endpoint (WOEID-based)
        # TR WOEID = 23424969, US = 23424977
        woeid_map = {
            "TR": 23424969, "US": 23424977, "UK": 23424975,
            "DE": 23424829, "FR": 23424819, "JP": 23424856,
        }
        woeid = woeid_map.get(TRENDS_REGION, 1)  # 1 = worldwide

        try:
            resp = requests.get(
                f"https://api.twitter.com/1.1/trends/place.json",
                params={"id": woeid},
                headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            logger.exception("Twitter API trends fetch failed")
            raise

        items: list[TrendItem] = []
        if data and isinstance(data, list) and data[0].get("trends"):
            for trend in data[0]["trends"][:15]:
                name = trend.get("name", "")
                tweet_volume = trend.get("tweet_volume") or 0
                url = trend.get("url", "")

                items.append(TrendItem(
                    title=name,
                    platform=TrendPlatform.TWITTER,
                    category=_guess_category(name, ""),
                    hashtags=[name] if name.startswith("#") else [],
                    url=url,
                    engagement=tweet_volume,
                    region=TRENDS_REGION,
                ))

        return items

    @staticmethod
    def from_api_response(raw: list[dict[str, Any]]) -> list[TrendItem]:
        """Parse raw API response dicts into TrendItem instances."""
        return [
            TrendItem(
                title=item.get("title", ""),
                platform=TrendPlatform(item.get("platform", "google")),
                category=item.get("category", "general"),
                description=item.get("description", ""),
                hashtags=item.get("hashtags", []),
                image_url=item.get("image_url", ""),
                url=item.get("url", ""),
                engagement=item.get("engagement", 0),
                region=item.get("region", "global"),
            )
            for item in raw
        ]


def _guess_category(title: str, description: str) -> str:
    """Simple heuristic to categorize a trend."""
    text = (title + " " + description).lower()

    keywords = {
        "dance": ["dans", "dance", "choreography", "koreografi"],
        "music": ["sarki", "song", "music", "muzik", "album", "concert", "konser"],
        "challenge": ["challenge", "akimi", "trend", "viral"],
        "meme": ["meme", "komik", "funny", "espri"],
        "sports": ["mac", "gol", "futbol", "basketball", "football", "score", "transfer"],
        "food": ["yemek", "tarif", "recipe", "food", "restaurant"],
        "fashion": ["moda", "fashion", "outfit", "style", "kiyafet"],
        "tech": ["iphone", "samsung", "ai", "yapay zeka", "uygulama", "app"],
        "entertainment": ["dizi", "film", "movie", "series", "oyuncu", "actor"],
    }

    for category, words in keywords.items():
        if any(w in text for w in words):
            return category

    return "general"
