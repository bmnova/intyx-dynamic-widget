"""News data source connector — NewsAPI.org integration."""

from __future__ import annotations

import logging
from typing import Any, Callable

import requests

from server.config import NEWS_API_COUNTRY, NEWS_API_KEY
from server.models import NewsData

logger = logging.getLogger(__name__)

NEWSAPI_BASE = "https://newsapi.org/v2"


class NewsSource:
    """Fetches and distributes news data to subscribers."""

    def __init__(self, fetch_fn: Callable[[], list[NewsData]] | None = None):
        self._fetch_fn = fetch_fn or self._default_fetch
        self._subscribers: list[Callable[[list[NewsData]], None]] = []
        self._last_data: list[NewsData] = []

    async def fetch(self) -> list[NewsData]:
        data = self._fetch_fn()
        self._last_data = data
        self._notify(data)
        return data

    def subscribe(self, callback: Callable[[list[NewsData]], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            self._subscribers.remove(callback)

        return unsubscribe

    @property
    def last_data(self) -> list[NewsData]:
        return self._last_data

    def _notify(self, data: list[NewsData]) -> None:
        for cb in self._subscribers:
            cb(data)

    @staticmethod
    def _default_fetch() -> list[NewsData]:
        """Fetch top headlines from NewsAPI.org."""
        if not NEWS_API_KEY:
            logger.debug("NEWS_API_KEY not set — returning empty news")
            return []

        try:
            resp = requests.get(
                f"{NEWSAPI_BASE}/top-headlines",
                params={"country": NEWS_API_COUNTRY, "pageSize": 20, "apiKey": NEWS_API_KEY},
                timeout=10,
            )
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            return NewsSource.from_api_response(articles)
        except Exception:
            logger.exception("NewsAPI fetch failed")
            return []

    @staticmethod
    def fetch_headlines(
        country: str | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Fetch top headlines filtered by country and/or category."""
        if not NEWS_API_KEY:
            return {"error": "NEWS_API_KEY not configured", "articles": []}

        params: dict[str, Any] = {"pageSize": min(limit, 100), "apiKey": NEWS_API_KEY}
        if country:
            params["country"] = country
        else:
            params["country"] = NEWS_API_COUNTRY
        if category:
            params["category"] = category

        try:
            resp = requests.get(f"{NEWSAPI_BASE}/top-headlines", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            return {
                "total_results": data.get("totalResults", len(articles)),
                "country": params.get("country"),
                "category": category,
                "articles": [
                    {
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "") if isinstance(a.get("source"), dict) else "",
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                    }
                    for a in articles
                    if a.get("title") and "[Removed]" not in (a.get("title") or "")
                ],
            }
        except Exception:
            logger.exception("NewsAPI fetch_headlines failed")
            return {"error": "Failed to fetch headlines", "articles": []}

    @staticmethod
    def search_news(query: str, limit: int = 10) -> dict[str, Any]:
        """Search news articles by keyword using NewsAPI everything endpoint."""
        if not NEWS_API_KEY:
            return {"error": "NEWS_API_KEY not configured", "articles": []}

        try:
            resp = requests.get(
                f"{NEWSAPI_BASE}/everything",
                params={
                    "q": query,
                    "pageSize": min(limit, 100),
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": NEWS_API_KEY,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            return {
                "query": query,
                "total_results": data.get("totalResults", len(articles)),
                "articles": [
                    {
                        "title": a.get("title", ""),
                        "description": a.get("description", ""),
                        "source": a.get("source", {}).get("name", "") if isinstance(a.get("source"), dict) else "",
                        "url": a.get("url", ""),
                        "published_at": a.get("publishedAt", ""),
                    }
                    for a in articles
                    if a.get("title") and "[Removed]" not in (a.get("title") or "")
                ],
            }
        except Exception:
            logger.exception("NewsAPI search_news failed for query: %s", query)
            return {"error": "Failed to search news", "articles": []}

    @staticmethod
    def from_api_response(raw: list[dict[str, Any]]) -> list[NewsData]:
        return [
            NewsData(
                headline=item.get("title") or item.get("headline", ""),
                category=item.get("category", "general"),
                source=item.get("source", {}).get("name", "") if isinstance(item.get("source"), dict) else item.get("source", ""),
                url=item.get("url", ""),
            )
            for item in raw
            if item.get("title")
        ]
