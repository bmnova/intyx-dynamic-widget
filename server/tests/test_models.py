"""Tests for data models."""

import time

from server.models import (
    HoroscopeData,
    NewsData,
    TriggerContext,
    UserAction,
    WeatherCondition,
    WeatherData,
    WidgetAction,
    WidgetActionType,
    WidgetCategory,
    WidgetContent,
    WidgetDefinition,
)


class TestWeatherData:
    def test_create(self):
        data = WeatherData(
            location="Istanbul",
            temperature=25.0,
            condition=WeatherCondition.SUNNY,
            humidity=50.0,
        )
        assert data.location == "Istanbul"
        assert data.temperature == 25.0
        assert data.condition == WeatherCondition.SUNNY

    def test_default_timestamp(self):
        before = time.time()
        data = WeatherData("Test", 0.0, WeatherCondition.CLOUDY, 0.0)
        after = time.time()
        assert before <= data.timestamp <= after


class TestNewsData:
    def test_create(self):
        data = NewsData(headline="Test", category="tech", source="CNN", url="https://example.com")
        assert data.headline == "Test"
        assert data.category == "tech"


class TestHoroscopeData:
    def test_create(self):
        data = HoroscopeData(sign="aries", prediction="Good day", date="2025-01-01", mood="happy")
        assert data.sign == "aries"
        assert data.mood == "happy"


class TestWidgetDefinition:
    def test_create_and_serialize(self):
        action = WidgetAction(
            type=WidgetActionType.OPEN_URL,
            label="Open",
            target="https://example.com",
        )
        content = WidgetContent(
            title="Test Widget",
            description="A test widget",
            actions=[action],
        )
        widget = WidgetDefinition(
            id="w1",
            name="test",
            category=WidgetCategory.INFORMATIONAL,
            content=content,
            priority=10,
        )

        d = widget.to_dict()
        assert d["id"] == "w1"
        assert d["category"] == "informational"
        assert d["content"]["title"] == "Test Widget"
        assert len(d["content"]["actions"]) == 1
        assert d["content"]["actions"][0]["type"] == "open_url"
        assert d["priority"] == 10


class TestTriggerContext:
    def test_create_minimal(self):
        ctx = TriggerContext(current_date="2025-01-01")
        assert ctx.current_date == "2025-01-01"
        assert ctx.weather is None
        assert ctx.news == []
        assert ctx.dismissed_widgets == set()

    def test_create_full(self):
        weather = WeatherData("Istanbul", 20.0, WeatherCondition.RAINY, 80.0)
        ctx = TriggerContext(
            current_date="2025-10-31",
            weather=weather,
            dismissed_widgets={"w1", "w2"},
            developer_params={"premium": True},
        )
        assert ctx.weather.temperature == 20.0
        assert "w1" in ctx.dismissed_widgets


class TestUserAction:
    def test_to_dict(self):
        action = UserAction(action="purchase", metadata={"item": "shoes"})
        d = action.to_dict()
        assert d["action"] == "purchase"
        assert d["metadata"]["item"] == "shoes"
        assert "timestamp" in d
