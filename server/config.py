"""Configuration for the Dynamic Widget MCP server."""

import logging
import os
import sys
from pathlib import Path

# Load .env from repo root and server/ so that `python -m server.app` or `flask run` use them
def _load_dotenv():
    try:
        from dotenv import load_dotenv
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env")
        load_dotenv(Path(__file__).resolve().parent / ".env")
    except ImportError:
        pass


_load_dotenv()

# Firebase
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "intyx-dynamic-widget")
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")

# Data source polling intervals (seconds)
WEATHER_POLL_INTERVAL = int(os.environ.get("WEATHER_POLL_INTERVAL", "300"))
NEWS_POLL_INTERVAL = int(os.environ.get("NEWS_POLL_INTERVAL", "600"))
HOROSCOPE_POLL_INTERVAL = int(os.environ.get("HOROSCOPE_POLL_INTERVAL", "3600"))

# Weather API
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# Trends
TRENDS_POLL_INTERVAL = int(os.environ.get("TRENDS_POLL_INTERVAL", "900"))  # 15 min
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "")
TRENDS_REGION = os.environ.get("TRENDS_REGION", "TR")  # ISO country code

# Server
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8080"))

# Rate limiting
RATE_LIMIT_DEFAULT = os.environ.get("RATE_LIMIT_DEFAULT", "200 per hour")
RATE_LIMIT_AI = os.environ.get("RATE_LIMIT_AI", "30 per minute")

# API key for server endpoints (set to empty string to disable auth)
SERVER_API_KEY = os.environ.get("INTYX_SERVER_API_KEY", "")

# Paddle webhook verification
PADDLE_WEBHOOK_SECRET = os.environ.get("PADDLE_WEBHOOK_SECRET", "")

# Sentry error tracking (optional)
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

# News API (newsapi.org)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
NEWS_API_COUNTRY = os.environ.get("NEWS_API_COUNTRY", "tr")


def validate_config() -> None:
    """Validate that required environment variables are set. Call at startup."""
    logger = logging.getLogger(__name__)
    warnings = []

    if not FIREBASE_CREDENTIALS_PATH:
        warnings.append("FIREBASE_CREDENTIALS_PATH not set — using Application Default Credentials")

    if not OPENWEATHER_API_KEY:
        warnings.append("OPENWEATHER_API_KEY not set — weather data will use placeholders")

    if not SERVER_API_KEY:
        warnings.append("INTYX_SERVER_API_KEY not set — API endpoints are unprotected (TODO: test sonrası ekleyin)")

    for w in warnings:
        logger.warning("CONFIG: %s", w)

    # Hard failures
    if not FIREBASE_PROJECT_ID:
        logger.error("FIREBASE_PROJECT_ID is required but not set")
        sys.exit(1)
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is required (AI widget suggestions and agent tasks)")
        sys.exit(1)
