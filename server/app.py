"""Flask application for the Dynamic Widget System."""

from __future__ import annotations

from flask import Flask, jsonify

from server.config import HOST, PORT


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Register blueprints
    from server.routes.widgets import widgets_bp
    from server.routes.ai import ai_bp
    from server.routes.licenses import licenses_bp

    app.register_blueprint(widgets_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(licenses_bp)

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "intyx-dynamic-widget"})

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT, debug=True)
