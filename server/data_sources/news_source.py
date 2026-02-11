"""News data source connector."""

from __future__ import annotations

from typing import Any, Callable

from server.models import NewsData


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
        return []

    @staticmethod
    def from_api_response(raw: list[dict[str, Any]]) -> list[NewsData]:
        return [
            NewsData(
                headline=item.get("headline", ""),
                category=item.get("category", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
            )
            for item in raw
        ]
