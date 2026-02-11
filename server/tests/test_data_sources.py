"""Tests for data source connectors."""

import asyncio

from server.data_sources.horoscope_source import HoroscopeSource
from server.data_sources.news_source import NewsSource
from server.data_sources.weather_source import WeatherSource
from server.models import HoroscopeData, NewsData, WeatherCondition, WeatherData


class TestWeatherSource:
    def test_default_fetch(self):
        source = WeatherSource()
        data = asyncio.get_event_loop().run_until_complete(source.fetch())
        assert isinstance(data, WeatherData)
        assert data.location == "Istanbul"

    def test_custom_fetch(self):
        custom_data = WeatherData("Ankara", 30.0, WeatherCondition.SUNNY, 40.0)
        source = WeatherSource(fetch_fn=lambda: custom_data)
        data = asyncio.get_event_loop().run_until_complete(source.fetch())
        assert data.location == "Ankara"
        assert data.temperature == 30.0

    def test_subscriber(self):
        received = []
        source = WeatherSource()
        source.subscribe(lambda d: received.append(d))
        asyncio.get_event_loop().run_until_complete(source.fetch())
        assert len(received) == 1
        assert received[0].location == "Istanbul"

    def test_unsubscribe(self):
        received = []
        source = WeatherSource()
        unsub = source.subscribe(lambda d: received.append(d))
        unsub()
        asyncio.get_event_loop().run_until_complete(source.fetch())
        assert len(received) == 0

    def test_from_api_response(self):
        raw = {"location": "Izmir", "temperature": 28, "condition": "sunny", "humidity": 55}
        data = WeatherSource.from_api_response(raw)
        assert data.location == "Izmir"
        assert data.condition == WeatherCondition.SUNNY

    def test_last_data(self):
        source = WeatherSource()
        assert source.last_data is None
        asyncio.get_event_loop().run_until_complete(source.fetch())
        assert source.last_data is not None


class TestNewsSource:
    def test_default_fetch(self):
        source = NewsSource()
        data = asyncio.get_event_loop().run_until_complete(source.fetch())
        assert isinstance(data, list)

    def test_from_api_response(self):
        raw = [{"headline": "Test", "category": "tech", "source": "CNN", "url": "https://example.com"}]
        data = NewsSource.from_api_response(raw)
        assert len(data) == 1
        assert data[0].headline == "Test"


class TestHoroscopeSource:
    def test_default_fetch(self):
        source = HoroscopeSource()
        data = asyncio.get_event_loop().run_until_complete(source.fetch("aries"))
        assert isinstance(data, HoroscopeData)
        assert data.sign == "aries"

    def test_get_last(self):
        source = HoroscopeSource()
        assert source.get_last("aries") is None
        asyncio.get_event_loop().run_until_complete(source.fetch("aries"))
        assert source.get_last("aries") is not None
        assert source.get_last("taurus") is None
