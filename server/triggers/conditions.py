"""Trigger condition implementations for the dynamic widget system."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from server.models import TriggerContext, TriggerType, WeatherCondition


class TriggerCondition:
    """Base class for all trigger conditions."""

    trigger_type: TriggerType

    def evaluate(self, ctx: TriggerContext) -> bool:
        raise NotImplementedError


class SeasonalCondition(TriggerCondition):
    """Activates based on calendar date ranges (e.g. Halloween, New Year)."""

    trigger_type = TriggerType.CONTEXTUAL

    def __init__(self, event: str, start_date: str, end_date: str):
        self.event = event
        self.start_date = start_date  # MM-DD
        self.end_date = end_date      # MM-DD

    def evaluate(self, ctx: TriggerContext) -> bool:
        today = datetime.fromisoformat(ctx.current_date).date()
        year = today.year
        start = date(year, *map(int, self.start_date.split("-")))
        end = date(year, *map(int, self.end_date.split("-")))
        return start <= today <= end

    def __repr__(self) -> str:
        return f"SeasonalCondition(event={self.event!r}, {self.start_date}..{self.end_date})"


class WeatherMatchCondition(TriggerCondition):
    """Activates when current weather matches specified criteria."""

    trigger_type = TriggerType.CONTEXTUAL

    def __init__(
        self,
        condition: WeatherCondition | None = None,
        min_temp: float | None = None,
        max_temp: float | None = None,
    ):
        self.condition = condition
        self.min_temp = min_temp
        self.max_temp = max_temp

    def evaluate(self, ctx: TriggerContext) -> bool:
        if ctx.weather is None:
            return False
        if self.condition and ctx.weather.condition != self.condition:
            return False
        if self.min_temp is not None and ctx.weather.temperature < self.min_temp:
            return False
        if self.max_temp is not None and ctx.weather.temperature > self.max_temp:
            return False
        return True


class UserActionCondition(TriggerCondition):
    """Activates when user has performed a specific action pattern."""

    trigger_type = TriggerType.USER_ACTION

    def __init__(self, action_pattern: str, min_occurrences: int = 1):
        self.action_pattern = action_pattern
        self.min_occurrences = min_occurrences

    def evaluate(self, ctx: TriggerContext) -> bool:
        count = sum(
            1 for a in ctx.user_actions if a.get("action") == self.action_pattern
        )
        return count >= self.min_occurrences


class DeveloperParamCondition(TriggerCondition):
    """Activates when a developer-defined parameter matches a specific value."""

    trigger_type = TriggerType.DEVELOPER_PARAM

    def __init__(self, param_key: str, param_value: Any):
        self.param_key = param_key
        self.param_value = param_value

    def evaluate(self, ctx: TriggerContext) -> bool:
        return ctx.developer_params.get(self.param_key) == self.param_value


def build_conditions(raw_conditions: list[dict]) -> list[TriggerCondition]:
    """Build TriggerCondition instances from raw config dicts.

    Shared by both REST API routes and MCP server.
    """
    conditions: list[TriggerCondition] = []
    for c in raw_conditions:
        ctype = c.get("type")
        if ctype == "seasonal":
            conditions.append(SeasonalCondition(
                event=c.get("event", ""),
                start_date=c.get("start_date", ""),
                end_date=c.get("end_date", ""),
            ))
        elif ctype == "weather":
            condition = None
            if c.get("condition"):
                condition = WeatherCondition(c["condition"])
            conditions.append(WeatherMatchCondition(
                condition=condition,
                min_temp=c.get("min_temp"),
                max_temp=c.get("max_temp"),
            ))
        elif ctype == "user_action":
            conditions.append(UserActionCondition(
                action_pattern=c.get("action_pattern", ""),
                min_occurrences=c.get("min_occurrences", 1),
            ))
        elif ctype == "developer_param":
            conditions.append(DeveloperParamCondition(
                param_key=c.get("param_key", ""),
                param_value=c.get("param_value"),
            ))
    return conditions
