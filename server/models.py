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


class TrendPlatform(Enum):
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    GOOGLE = "google"


@dataclass
class TrendItem:
    """A single viral/trending topic from social media."""
    title: str
    platform: TrendPlatform
    category: str  # dance, music, challenge, meme, news, etc.
    description: str = ""
    hashtags: list[str] = field(default_factory=list)
    image_url: str = ""
    url: str = ""
    engagement: int = 0  # likes, views, shares etc.
    region: str = "global"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "platform": self.platform.value,
            "category": self.category,
            "description": self.description,
            "hashtags": self.hashtags,
            "image_url": self.image_url,
            "url": self.url,
            "engagement": self.engagement,
            "region": self.region,
            "timestamp": self.timestamp,
        }


# --- Color Palette ---


@dataclass
class ColorPalette:
    """Color palette that widgets use to match the host app's design system."""

    primary: str = "#6200EE"
    primary_variant: str = "#3700B3"
    secondary: str = "#03DAC6"
    secondary_variant: str = "#018786"
    background: str = "#FFFFFF"
    surface: str = "#FFFFFF"
    error: str = "#B00020"
    on_primary: str = "#FFFFFF"
    on_secondary: str = "#000000"
    on_background: str = "#000000"
    on_surface: str = "#000000"
    on_error: str = "#FFFFFF"
    border_radius: float = 12.0
    elevation: float = 2.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary": self.primary,
            "primary_variant": self.primary_variant,
            "secondary": self.secondary,
            "secondary_variant": self.secondary_variant,
            "background": self.background,
            "surface": self.surface,
            "error": self.error,
            "on_primary": self.on_primary,
            "on_secondary": self.on_secondary,
            "on_background": self.on_background,
            "on_surface": self.on_surface,
            "on_error": self.on_error,
            "border_radius": self.border_radius,
            "elevation": self.elevation,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ColorPalette:
        return ColorPalette(**{k: v for k, v in data.items() if k in ColorPalette.__dataclass_fields__})


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
    trends: list[TrendItem] = field(default_factory=list)
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
