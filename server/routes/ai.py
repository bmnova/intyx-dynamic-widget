"""AI-powered widget endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server.ai.gemini_client import GeminiClient

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

_client: GeminiClient | None = None


def _get_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


@ai_bp.route("/suggest-widget", methods=["POST"])
def suggest_widget():
    """Use AI to suggest which widget(s) to show based on context."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Context required"}), 400

    client = _get_client()
    result = client.suggest_widgets(data)
    return jsonify(result)


@ai_bp.route("/generate-content", methods=["POST"])
def generate_content():
    """Use AI to generate widget content."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    widget_type = data.get("widget_type")
    context = data.get("context", {})
    if not widget_type:
        return jsonify({"error": "widget_type required"}), 400

    client = _get_client()
    result = client.generate_widget_content(widget_type, context)
    return jsonify(result)
