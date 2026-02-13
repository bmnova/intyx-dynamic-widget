"""Trend/viral content API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

trends_bp = Blueprint("trends", __name__, url_prefix="/api/trends")


@trends_bp.route("", methods=["GET"])
def get_trends():
    """Get current cached trends.

    Query params:
        category: Filter by category (dance, music, challenge, etc.)
        platform: Filter by platform (tiktok, twitter, google, etc.)
        limit: Max items to return (default 10)
    """
    cached = fb.get_cached_data("trends")
    if not cached:
        return jsonify({"items": [], "count": 0})

    items = cached.get("items", [])

    # Optional filters
    category = request.args.get("category")
    platform = request.args.get("platform")
    limit = int(request.args.get("limit", 10))

    if category:
        items = [t for t in items if t.get("category") == category]
    if platform:
        items = [t for t in items if t.get("platform") == platform]

    items = items[:limit]

    return jsonify({
        "items": items,
        "count": len(items),
        "updated_at": cached.get("timestamp"),
    })


@trends_bp.route("/categories", methods=["GET"])
def get_trend_categories():
    """Get available trend categories and their counts."""
    cached = fb.get_cached_data("trends")
    if not cached:
        return jsonify({"categories": {}})

    items = cached.get("items", [])
    categories: dict[str, int] = {}
    for item in items:
        cat = item.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    return jsonify({"categories": categories})


@trends_bp.route("/suggest", methods=["POST"])
def suggest_from_trends():
    """Use AI to suggest widgets based on current trends + app context.

    Body: {
        "context": { "app_type": "video_generation", ... },
        "trend_filter": { "category": "dance", "limit": 5 }  // optional
    }
    """
    data = request.get_json() or {}
    context = data.get("context", {})
    trend_filter = data.get("trend_filter", {})

    # Get current trends
    cached = fb.get_cached_data("trends")
    trend_items = cached.get("items", []) if cached else []

    # Apply optional filter
    if trend_filter.get("category"):
        trend_items = [t for t in trend_items if t.get("category") == trend_filter["category"]]
    trend_limit = trend_filter.get("limit", 5)
    trend_items = trend_items[:trend_limit]

    # Enrich context with trends
    enriched_context = {
        **context,
        "viral_trends": trend_items,
    }

    # Let AI suggest widgets based on trends
    from server.ai.gemini_client import get_gemini_client
    client = get_gemini_client()
    result = client.suggest_widgets(enriched_context)
    return jsonify(result)
