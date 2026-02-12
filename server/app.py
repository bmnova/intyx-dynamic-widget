"""Flask application for the Dynamic Widget System."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from server.config import (
    HOST,
    PORT,
    RATE_LIMIT_DEFAULT,
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

    app = Flask(__name__)
    CORS(app)

    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[RATE_LIMIT_DEFAULT],
        storage_uri="memory://",
    )

    # API key validation middleware
    @app.before_request
    def _check_api_key():
        # Skip auth for health check and license validation/creation
        skip_paths = ("/api/health", "/api/licenses/validate", "/api/licenses")
        if request.path in skip_paths:
            return None

        # Skip if SERVER_API_KEY is not configured (development mode)
        if not SERVER_API_KEY:
            return None

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        else:
            # Fallback: check api_key in query params or body for backward compat
            token = request.args.get("api_key", "")
            if not token:
                body = request.get_json(silent=True) or {}
                token = body.get("api_key", "")

        if not token or token != SERVER_API_KEY:
            return jsonify({"error": "Unauthorized — invalid or missing API key"}), 401

        return None

    # Register blueprints
    from server.routes.widgets import widgets_bp
    from server.routes.ai import ai_bp
    from server.routes.licenses import licenses_bp
    from server.routes.agent_tasks import agent_tasks_bp

    app.register_blueprint(widgets_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(licenses_bp)
    app.register_blueprint(agent_tasks_bp)

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


if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=True)
