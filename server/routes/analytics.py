"""Widget analytics endpoint — returns interaction stats for the caller's widgets."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _get_api_key() -> str | None:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip() or None
    return None


@analytics_bp.route("/widgets", methods=["GET"])
def widget_analytics():
    """Aggregate interaction data for the caller's widgets.
    ---
    tags:
      - Analytics
    summary: Widget interaction analytics
    description: >
      Returns per-widget and aggregate interaction counts (impression, tap,
      dismiss, etc.) for all widgets owned by the authenticated license key.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Analytics data.
        schema:
          type: object
          properties:
            widget_count:
              type: integer
            totals:
              type: object
            by_widget:
              type: object
      401:
        description: Missing or invalid API key.
    """
    api_key = _get_api_key()
    if not api_key:
        return jsonify({"error": "Authorization header required"}), 401

    data = fb.get_widget_analytics(api_key)
    return jsonify(data)
