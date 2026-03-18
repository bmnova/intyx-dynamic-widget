"""AI-powered widget endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb
from server.ai.gemini_client import get_gemini_client

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


def _check_ai_quota() -> tuple[str | None, dict | None]:
    """Extract license key and enforce the plan's monthly AI call quota.

    Returns ``(license_key, None)`` when the call is allowed, or
    ``(None, error_response)`` when the limit is exceeded or the key is
    unrecognisable.  Admin server keys (non-intyx_ tokens) bypass the
    quota entirely.
    """
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else request.args.get("api_key", "")

    # Non-license tokens (admin key, dev mode) → skip quota
    if not token.startswith("intyx_"):
        return token or None, None

    lic = fb.get_license(token)
    if not lic or not lic.get("active"):
        return None, (jsonify({"error": "Unauthorized — invalid or inactive license key"}), 401)

    monthly_limit = lic.get("ai_calls_limit", 50)  # safe default for old licenses
    allowed = fb.try_consume_ai_call(token, monthly_limit)
    if not allowed:
        limit_display = str(monthly_limit) if monthly_limit != -1 else "unlimited"
        return None, (
            jsonify({
                "error": "AI call quota exceeded",
                "message": (
                    f"Your {lic.get('plan', 'current')} plan allows "
                    f"{limit_display} AI calls per month. "
                    "Upgrade your plan to continue using AI features."
                ),
                "ai_calls_limit": monthly_limit,
            }),
            429,
        )

    return token, None


@ai_bp.route("/suggest-widget", methods=["POST"])
def suggest_widget():
    """Use AI to suggest which widget(s) to show based on context.
    ---
    tags:
      - AI
    summary: AI widget suggestion
    description: >
      Sends the provided context to the Gemini AI model and returns a list
      of widgets best suited for the current user moment. Rate-limited more
      strictly than other endpoints.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: >
            Arbitrary context object. Common keys include `app_type`,
            `user_segment`, `current_screen`, `developer_task`, and
            contextual data such as weather or recent events.
          example:
            app_type: e-commerce
            user_segment: returning_buyer
            current_screen: checkout
    responses:
      200:
        description: AI-suggested widgets.
        schema:
          type: object
          properties:
            widgets:
              type: array
              items:
                type: object
      400:
        description: Context required.
      429:
        description: Rate limit exceeded.
    """
    _, err = _check_ai_quota()
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({"error": "Context required"}), 400

    client = get_gemini_client()
    result = client.suggest_widgets(data)
    return jsonify(result)


@ai_bp.route("/generate-content", methods=["POST"])
def generate_content():
    """Use AI to generate content for a specific widget type.
    ---
    tags:
      - AI
    summary: AI content generation
    description: >
      Given a widget type and context, the AI generates ready-to-use
      params (title, subtitle, image prompt, CTA text, etc.).
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - widget_type
          properties:
            widget_type:
              type: string
              description: One of the supported widget type identifiers.
              example: banner
            context:
              type: object
              description: Additional context to personalise the generated content.
              example:
                season: summer
                brand_tone: playful
    responses:
      200:
        description: Generated widget content.
        schema:
          type: object
      400:
        description: widget_type required.
      429:
        description: Rate limit exceeded.
    """
    _, err = _check_ai_quota()
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    widget_type = data.get("widget_type")
    context = data.get("context", {})
    if not widget_type:
        return jsonify({"error": "widget_type required"}), 400

    client = get_gemini_client()
    result = client.generate_widget_content(widget_type, context)
    return jsonify(result)
