"""Trend/viral content API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

trends_bp = Blueprint("trends", __name__, url_prefix="/api/trends")


@trends_bp.route("", methods=["GET"])
def get_trends():
    """Get current cached viral trends.
    ---
    tags:
      - Trends
    summary: List trends
    description: Returns the latest cached trends. Trends are refreshed
      periodically by a background job. Results can be filtered by
      category and/or platform.
    security:
      - BearerAuth: []
    parameters:
      - name: category
        in: query
        type: string
        required: false
        description: Filter by trend category (dance, music, challenge, meme, news, …).
        example: dance
      - name: platform
        in: query
        type: string
        required: false
        description: Filter by platform (tiktok, twitter, instagram, youtube, google).
        example: tiktok
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        description: Maximum number of trends to return.
    responses:
      200:
        description: Trend list.
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  title:
                    type: string
                  platform:
                    type: string
                  category:
                    type: string
                  description:
                    type: string
                  hashtags:
                    type: array
                    items:
                      type: string
                  engagement:
                    type: integer
                  region:
                    type: string
            count:
              type: integer
            updated_at:
              type: number
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
    """Get available trend categories and their item counts.
    ---
    tags:
      - Trends
    summary: List trend categories
    security:
      - BearerAuth: []
    responses:
      200:
        description: Category counts.
        schema:
          type: object
          properties:
            categories:
              type: object
              additionalProperties:
                type: integer
              example:
                dance: 12
                music: 8
                challenge: 5
    """
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
    """Use AI to suggest widgets based on current trends and app context.
    ---
    tags:
      - Trends
    summary: AI trend-based widget suggestion
    description: >
      Fetches the latest cached trends, optionally filters them, injects
      them into the AI context, and returns AI-recommended widgets tailored
      to what's viral right now.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            context:
              type: object
              description: App/user context to personalise suggestions.
              example:
                app_type: video_generation
                user_segment: creator
            trend_filter:
              type: object
              description: Optional filter applied to the trend list before AI processing.
              properties:
                category:
                  type: string
                  example: dance
                limit:
                  type: integer
                  default: 5
    responses:
      200:
        description: AI-suggested widgets based on current trends.
        schema:
          type: object
          properties:
            widgets:
              type: array
              items:
                type: object
      429:
        description: Rate limit exceeded.
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
