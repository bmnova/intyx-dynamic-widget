"""Data models for the Dynamic Widget System."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# --- Data Source Models ---

class WeatherCondition(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    WINDY = "windy"


@dataclass
class WeatherData:
    location: str
    temperature: float
    condition: WeatherCondition
    humidity: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class NewsData:
    headline: str
    category: str
    source: str
    url: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class HoroscopeData:
    sign: str
    prediction: str
    date: str
    mood: str


# --- Widget Models ---

class WidgetActionType(Enum):
    NAVIGATE = "navigate"
    OPEN_URL = "open_url"
    TRIGGER_FLOW = "trigger_flow"
    DISMISS = "dismiss"


class WidgetCategory(Enum):
    CONTEXTUAL = "contextual"
    PROMOTIONAL = "promotional"
    FUNCTIONAL = "functional"
    INFORMATIONAL = "informational"


@dataclass
class WidgetAction:
    type: WidgetActionType
    label: str
    target: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "label": self.label,
            "target": self.target,
            "metadata": self.metadata,
        }


@dataclass
class WidgetContent:
    title: str
    actions: list[WidgetAction]
    description: str = ""
    image_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "actions": [a.to_dict() for a in self.actions],
        }


@dataclass
class WidgetDefinition:
    id: str
    name: str
    category: WidgetCategory
    content: WidgetContent
    priority: int = 0
    ttl_ms: int | None = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "content": self.content.to_dict(),
            "priority": self.priority,
            "ttl_ms": self.ttl_ms,
            "created_at": self.created_at,
        }


# --- Trigger Models ---

class TriggerType(Enum):
    CONTEXTUAL = "contextual"
    USER_ACTION = "user_action"
    DEVELOPER_PARAM = "developer_param"


@dataclass
class TriggerContext:
    current_date: str  # ISO date string
    weather: WeatherData | None = None
    news: list[NewsData] = field(default_factory=list)
    horoscope: HoroscopeData | None = None
    user_actions: list[dict[str, Any]] = field(default_factory=list)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    dismissed_widgets: set[str] = field(default_factory=set)
    developer_params: dict[str, Any] = field(default_factory=dict)


# --- User State ---

@dataclass
class UserAction:
    action: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
