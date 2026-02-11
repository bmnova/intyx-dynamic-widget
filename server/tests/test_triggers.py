"""Tests for trigger engine and conditions."""

from server.models import (
    TriggerContext,
    WeatherCondition,
    WeatherData,
    WidgetCategory,
    WidgetContent,
    WidgetDefinition,
)
from server.triggers.conditions import (
    DeveloperParamCondition,
    SeasonalCondition,
    UserActionCondition,
    WeatherMatchCondition,
)
from server.triggers.engine import TriggerEngine, WidgetTriggerRule


def _make_widget(widget_id: str, priority: int = 0) -> WidgetDefinition:
    return WidgetDefinition(
        id=widget_id,
        name=widget_id,
        category=WidgetCategory.INFORMATIONAL,
        content=WidgetContent(title="Test", actions=[]),
        priority=priority,
    )


class TestSeasonalCondition:
    def test_match_halloween(self):
        cond = SeasonalCondition("halloween", "10-25", "11-01")
        ctx = TriggerContext(current_date="2025-10-31")
        assert cond.evaluate(ctx) is True

    def test_no_match_outside_range(self):
        cond = SeasonalCondition("halloween", "10-25", "11-01")
        ctx = TriggerContext(current_date="2025-12-01")
        assert cond.evaluate(ctx) is False


class TestWeatherMatchCondition:
    def test_match_condition(self):
        cond = WeatherMatchCondition(condition=WeatherCondition.RAINY)
        weather = WeatherData("Istanbul", 15.0, WeatherCondition.RAINY, 90.0)
        ctx = TriggerContext(current_date="2025-01-01", weather=weather)
        assert cond.evaluate(ctx) is True

    def test_no_match_wrong_condition(self):
        cond = WeatherMatchCondition(condition=WeatherCondition.SUNNY)
        weather = WeatherData("Istanbul", 15.0, WeatherCondition.RAINY, 90.0)
        ctx = TriggerContext(current_date="2025-01-01", weather=weather)
        assert cond.evaluate(ctx) is False

    def test_temperature_range(self):
        cond = WeatherMatchCondition(min_temp=10.0, max_temp=20.0)
        weather = WeatherData("Istanbul", 15.0, WeatherCondition.CLOUDY, 60.0)
        ctx = TriggerContext(current_date="2025-01-01", weather=weather)
        assert cond.evaluate(ctx) is True

    def test_no_weather_data(self):
        cond = WeatherMatchCondition(condition=WeatherCondition.SUNNY)
        ctx = TriggerContext(current_date="2025-01-01")
        assert cond.evaluate(ctx) is False


class TestUserActionCondition:
    def test_match_action(self):
        cond = UserActionCondition("purchase", min_occurrences=2)
        ctx = TriggerContext(
            current_date="2025-01-01",
            user_actions=[{"action": "purchase"}, {"action": "purchase"}, {"action": "view"}],
        )
        assert cond.evaluate(ctx) is True

    def test_insufficient_occurrences(self):
        cond = UserActionCondition("purchase", min_occurrences=3)
        ctx = TriggerContext(
            current_date="2025-01-01",
            user_actions=[{"action": "purchase"}],
        )
        assert cond.evaluate(ctx) is False


class TestDeveloperParamCondition:
    def test_match(self):
        cond = DeveloperParamCondition("premium", True)
        ctx = TriggerContext(current_date="2025-01-01", developer_params={"premium": True})
        assert cond.evaluate(ctx) is True

    def test_no_match(self):
        cond = DeveloperParamCondition("premium", True)
        ctx = TriggerContext(current_date="2025-01-01", developer_params={"premium": False})
        assert cond.evaluate(ctx) is False


class TestTriggerEngine:
    def test_evaluate_matches(self):
        engine = TriggerEngine()
        w1 = _make_widget("w1", priority=10)
        w2 = _make_widget("w2", priority=20)

        engine.register(WidgetTriggerRule(
            widget=w1,
            conditions=[WeatherMatchCondition(condition=WeatherCondition.RAINY)],
        ))
        engine.register(WidgetTriggerRule(
            widget=w2,
            conditions=[WeatherMatchCondition(condition=WeatherCondition.RAINY)],
        ))

        weather = WeatherData("Istanbul", 10.0, WeatherCondition.RAINY, 90.0)
        ctx = TriggerContext(current_date="2025-01-01", weather=weather)

        matched = engine.evaluate(ctx)
        assert len(matched) == 2
        assert matched[0].id == "w2"  # Higher priority first
        assert matched[1].id == "w1"

    def test_dismissed_widgets_filtered(self):
        engine = TriggerEngine()
        w1 = _make_widget("w1")
        engine.register(WidgetTriggerRule(
            widget=w1,
            conditions=[DeveloperParamCondition("show", True)],
        ))

        ctx = TriggerContext(
            current_date="2025-01-01",
            developer_params={"show": True},
            dismissed_widgets={"w1"},
        )
        matched = engine.evaluate(ctx)
        assert len(matched) == 0

    def test_match_mode_any(self):
        engine = TriggerEngine()
        w1 = _make_widget("w1")
        engine.register(WidgetTriggerRule(
            widget=w1,
            conditions=[
                WeatherMatchCondition(condition=WeatherCondition.SUNNY),
                DeveloperParamCondition("show", True),
            ],
            match_mode="any",
        ))

        ctx = TriggerContext(
            current_date="2025-01-01",
            developer_params={"show": True},
        )
        matched = engine.evaluate(ctx)
        assert len(matched) == 1

    def test_unregister(self):
        engine = TriggerEngine()
        w1 = _make_widget("w1")
        engine.register(WidgetTriggerRule(
            widget=w1,
            conditions=[DeveloperParamCondition("show", True)],
        ))
        assert len(engine.rules) == 1

        engine.unregister("w1")
        assert len(engine.rules) == 0

    def test_empty_conditions_no_match(self):
        engine = TriggerEngine()
        w1 = _make_widget("w1")
        engine.register(WidgetTriggerRule(widget=w1, conditions=[]))
        ctx = TriggerContext(current_date="2025-01-01")
        assert len(engine.evaluate(ctx)) == 0
