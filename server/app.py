"""Flask application for the Dynamic Widget System."""

from __future__ import annotations

import logging

from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from server.config import (
    DEV_MODE,
    HOST,
    PORT,
    RATE_LIMIT_DEFAULT,
    SENTRY_DSN,
    SERVER_API_KEY,
    validate_config,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    validate_config()

    # Sentry error tracking (optional)
    if SENTRY_DSN:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration

            sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()], traces_sample_rate=0.1)
            logging.getLogger(__name__).info("Sentry initialized")
        except ImportError:
            logging.getLogger(__name__).warning("sentry-sdk not installed — error tracking disabled")

    app = Flask(__name__)
    CORS(app)

    # ── OpenAPI / Swagger UI ─────────────────────────────────────────
    Swagger(
        app,
        config={
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec",
                    "route": "/api/docs/apispec.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "swagger_ui": True,
            "specs_route": "/api/docs/",
        },
        template={
            "swagger": "2.0",
            "info": {
                "title": "Intyx Dynamic Widget API",
                "description": (
                    "AI-driven dynamic widget system for Flutter apps.\n\n"
                    "**Authentication**: All endpoints except `/api/health`, "
                    "`/api/licenses/validate`, and `/api/licenses` require a "
                    "Bearer API key in the `Authorization` header."
                ),
                "version": "1.0.0",
                "contact": {"email": "support@intyx.dev"},
            },
            "securityDefinitions": {
                "BearerAuth": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "Format: `Bearer <api_key>`",
                }
            },
            "security": [{"BearerAuth": []}],
            "consumes": ["application/json"],
            "produces": ["application/json"],
        },
    )

    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[RATE_LIMIT_DEFAULT],
        storage_uri="memory://",
    )

    # ── Auth middleware ───────────────────────────────────────────────
    PUBLIC_PATHS = frozenset((
        "/api/health",
        "/api/licenses/validate",
        "/api/licenses",
        "/api/paddle/webhook",
    ))

    @app.before_request
    def _check_api_key():
        if request.path in PUBLIC_PATHS:
            return None

        # Extract token
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        else:
            token = request.args.get("api_key", "")
            if not token:
                body = request.get_json(silent=True) or {}
                token = body.get("api_key", "")

        if SERVER_API_KEY:
            # Server key matches → admin access
            if token == SERVER_API_KEY:
                return None
            # Valid license key → customer access
            if token.startswith("intyx_"):
                from server import firebase_client as fb
                lic = fb.get_cached_data(f"license:{token}")
                if lic and lic.get("active"):
                    return None
            return jsonify({"error": "Unauthorized — invalid or missing API key"}), 401

        # No server key — still accept valid license keys
        if token.startswith("intyx_"):
            from server import firebase_client as fb
            lic = fb.get_cached_data(f"license:{token}")
            if lic and lic.get("active"):
                return None

        # Allow unauthenticated requests only in explicit dev mode
        if DEV_MODE:
            return None

        return jsonify({"error": "Unauthorized — set INTYX_DEV_MODE=true for local development or provide a valid API key"}), 401

    # Register blueprints
    from server.routes.widgets import widgets_bp
    from server.routes.ai import ai_bp
    from server.routes.licenses import licenses_bp
    from server.routes.agent_tasks import agent_tasks_bp
    from server.routes.trends import trends_bp
    from server.routes.paddle_webhook import paddle_bp
    from server.routes.admin import admin_bp

    app.register_blueprint(widgets_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(licenses_bp)
    app.register_blueprint(agent_tasks_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(paddle_bp)
    app.register_blueprint(admin_bp)

    # Apply stricter rate limit to AI endpoints
    from server.config import RATE_LIMIT_AI
    limiter.limit(RATE_LIMIT_AI)(ai_bp)

    # Health check
    @app.route("/api/health")
    @limiter.exempt
    def health():
        return jsonify({"status": "ok", "service": "intyx-dynamic-widget"})

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Rate limit exceeded", "message": str(e.description)}), 429

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
