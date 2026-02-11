"""Configuration for the Dynamic Widget MCP server."""

import os

# Firebase
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "intyx-dynamic-widget")
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")

# Data source polling intervals (seconds)
WEATHER_POLL_INTERVAL = int(os.environ.get("WEATHER_POLL_INTERVAL", "300"))
NEWS_POLL_INTERVAL = int(os.environ.get("NEWS_POLL_INTERVAL", "600"))
HOROSCOPE_POLL_INTERVAL = int(os.environ.get("HOROSCOPE_POLL_INTERVAL", "3600"))

# Server
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))
