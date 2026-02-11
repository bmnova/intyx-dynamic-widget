"""Trigger evaluation engine — matches context against widget trigger rules."""

from __future__ import annotations

from dataclasses import dataclass

from server.models import TriggerContext, WidgetDefinition
from server.triggers.conditions import TriggerCondition


@dataclass
class WidgetTriggerRule:
    """Binds a widget to one or more trigger conditions."""

    widget: WidgetDefinition
    conditions: list[TriggerCondition]
    match_mode: str = "all"  # "all" or "any"

    def matches(self, ctx: TriggerContext) -> bool:
        if not self.conditions:
            return False
        if self.match_mode == "all":
            return all(c.evaluate(ctx) for c in self.conditions)
        return any(c.evaluate(ctx) for c in self.conditions)


class TriggerEngine:
    """Evaluates all registered trigger rules against a given context."""

    def __init__(self) -> None:
        self._rules: list[WidgetTriggerRule] = []

    def register(self, rule: WidgetTriggerRule) -> None:
        self._rules.append(rule)

    def unregister(self, widget_id: str) -> None:
        self._rules = [r for r in self._rules if r.widget.id != widget_id]

    def evaluate(self, ctx: TriggerContext) -> list[WidgetDefinition]:
        """Return all widgets whose trigger rules match the given context,
        sorted by priority (highest first) and filtered out dismissed widgets."""
        matched: list[WidgetDefinition] = []
        for rule in self._rules:
            if rule.widget.id in ctx.dismissed_widgets:
                continue
            if rule.matches(ctx):
                matched.append(rule.widget)
        matched.sort(key=lambda w: w.priority, reverse=True)
        return matched

    @property
    def rules(self) -> list[WidgetTriggerRule]:
        return list(self._rules)
