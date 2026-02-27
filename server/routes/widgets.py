"""Widget API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb
from server.ai.gemini_client import VALID_WIDGET_TYPES
from server.models import ColorPalette, TriggerContext, WeatherCondition, WeatherData
from server.triggers.conditions import build_conditions
from server.triggers.engine import TriggerEngine, WidgetTriggerRule

widgets_bp = Blueprint("widgets", __name__, url_prefix="/api/widgets")


def _get_license_key(body: dict | None = None) -> str | None:
    """Extract an intyx_* license key from the request (header → query → body)."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        if token.startswith("intyx_"):
            return token
    token = request.args.get("api_key", "")
    if token.startswith("intyx_"):
        return token
    if body:
        token = body.get("api_key", "")
        if isinstance(token, str) and token.startswith("intyx_"):
            return token
    return None


@widgets_bp.route("", methods=["GET"])
def list_widgets():
    """List all active widgets.
    ---
    tags:
      - Widgets
    summary: List widgets
    description: Returns all active widgets sorted by priority, optionally
      filtered by user (dismissed widgets are excluded).
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: query
        type: string
        required: false
        description: Exclude widgets already dismissed by this user.
      - name: limit
        in: query
        type: integer
        required: false
        default: 100
        description: Maximum number of widgets to return (capped at 500).
      - name: offset
        in: query
        type: integer
        required: false
        default: 0
        description: Number of widgets to skip for pagination.
    responses:
      200:
        description: Widget list.
        schema:
          type: object
          properties:
            widgets:
              type: array
              items:
                type: object
            limit:
              type: integer
            offset:
              type: integer
      401:
        description: Unauthorized.
    """
    user_id = request.args.get("user_id")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = int(request.args.get("offset", 0))

    widgets = fb.get_widgets(limit=limit, offset=offset)

    if user_id:
        user_state = fb.get_user_state(user_id)
        dismissed = set(user_state.get("dismissed_widgets", []))
        widgets = [w for w in widgets if w["id"] not in dismissed]

    widgets.sort(key=lambda w: w.get("priority", 0), reverse=True)
    return jsonify({"widgets": widgets, "limit": limit, "offset": offset})


@widgets_bp.route("/<widget_id>", methods=["GET"])
def get_widget(widget_id: str):
    """Get a single widget definition.
    ---
    tags:
      - Widgets
    summary: Get widget by ID
    security:
      - BearerAuth: []
    parameters:
      - name: widget_id
        in: path
        type: string
        required: true
        description: Widget identifier.
    responses:
      200:
        description: Widget definition.
        schema:
          type: object
      404:
        description: Widget not found.
    """
    widget = fb.get_widget(widget_id)
    if not widget:
        return jsonify({"error": "Widget not found"}), 404
    return jsonify(widget)


@widgets_bp.route("", methods=["POST"])
def create_widget():
    """Create a new widget definition.
    ---
    tags:
      - Widgets
    summary: Create widget
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - type
            - params
          properties:
            type:
              type: string
              description: Widget type (e.g. banner, promotional, countdown_banner).
              example: banner
            params:
              type: object
              description: Widget-type-specific parameters.
              example:
                title: "Summer Sale"
                subtitle: "Up to 50% off"
            priority:
              type: integer
              description: Display priority (higher = shown first).
              default: 0
            color_palette:
              type: object
              description: Optional color overrides for this widget.
            license_key:
              type: string
              description: Your intyx_* API key for plan-limit enforcement.
    responses:
      201:
        description: Widget created.
        schema:
          type: object
          properties:
            id:
              type: string
            message:
              type: string
      400:
        description: Validation error.
      403:
        description: Widget limit reached for the current plan.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ["type", "params"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Plan limit enforcement
    license_key = data.get("license_key") or request.args.get("api_key", "")
    if license_key:
        lic = fb.get_license(license_key) if license_key.startswith("intyx_") else None
        if lic:
            widget_limit = lic.get("widget_limit", -1)
            if widget_limit > 0:
                current_count = fb.count_widgets_for_license(license_key)
                if current_count >= widget_limit:
                    return jsonify({
                        "error": f"Widget limit reached ({widget_limit}). Upgrade your plan.",
                        "current": current_count,
                        "limit": widget_limit,
                    }), 403
            data["license_key"] = license_key

    # Validate widget type against catalog
    widget_type = data["type"]
    if widget_type not in VALID_WIDGET_TYPES:
        return jsonify({
            "error": f"Unknown widget type: {widget_type}",
            "valid_types": sorted(VALID_WIDGET_TYPES),
        }), 400

    # Validate params is a dict
    if not isinstance(data["params"], dict):
        return jsonify({"error": "params must be a JSON object"}), 400

    # Normalize color_palette into common params if provided
    if "color_palette" in data and data["color_palette"]:
        palette = ColorPalette.from_dict(data["color_palette"])
        common = data.setdefault("common", {})
        common["color_palette"] = palette.to_dict()

    widget_id = fb.create_widget(data)
    return jsonify({"id": widget_id, "message": "Widget created"}), 201


@widgets_bp.route("/<widget_id>", methods=["PUT"])
def update_widget(widget_id: str):
    """Update an existing widget.
    ---
    tags:
      - Widgets
    summary: Update widget
    security:
      - BearerAuth: []
    parameters:
      - name: widget_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Fields to update (partial update supported).
    responses:
      200:
        description: Widget updated.
      404:
        description: Widget not found.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    if fb.update_widget(widget_id, data):
        return jsonify({"message": "Widget updated"})
    return jsonify({"error": "Widget not found"}), 404


@widgets_bp.route("/<widget_id>", methods=["DELETE"])
def delete_widget(widget_id: str):
    """Delete a widget.
    ---
    tags:
      - Widgets
    summary: Delete widget
    security:
      - BearerAuth: []
    parameters:
      - name: widget_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Widget deleted.
      404:
        description: Widget not found.
    """
    if fb.delete_widget(widget_id):
        return jsonify({"message": "Widget deleted"})
    return jsonify({"error": "Widget not found"}), 404


@widgets_bp.route("/evaluate", methods=["POST"])
def evaluate_triggers():
    """Evaluate trigger rules against context and return matching widgets.
    ---
    tags:
      - Widgets
    summary: Evaluate triggers
    description: Runs all stored trigger rules against the provided context
      and returns widgets whose conditions are satisfied.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_date
          properties:
            current_date:
              type: string
              description: ISO 8601 date string (e.g. "2026-02-23").
              example: "2026-02-23"
            weather:
              type: object
              description: Current weather data.
              properties:
                location:
                  type: string
                temperature:
                  type: number
                condition:
                  type: string
                  enum: [sunny, cloudy, rainy, snowy, stormy, windy]
                humidity:
                  type: number
            user_actions:
              type: array
              items:
                type: object
              description: Recent user actions for trigger evaluation.
            user_preferences:
              type: object
              description: Arbitrary key/value preferences.
            dismissed_widgets:
              type: array
              items:
                type: string
              description: Widget IDs the user has already dismissed.
            developer_params:
              type: object
              description: Custom parameters passed by the host app.
    responses:
      200:
        description: Matching widgets.
        schema:
          type: object
          properties:
            widgets:
              type: array
              items:
                type: object
      400:
        description: Context required.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Context required"}), 400

    # ── MAU limit check ──────────────────────────────────────────────
    license_key = _get_license_key(data)
    if license_key:
        lic = fb.get_license(license_key)
        if lic:
            mau_limit = lic.get("mau_limit", -1)
            if mau_limit > 0:
                usage = fb.get_usage(license_key)
                if len(usage.get("unique_users", [])) >= mau_limit:
                    return jsonify({
                        "widgets": [],
                        "fallback": True,
                        "reason": "limit_exceeded",
                    })

    # Build TriggerContext from request
    weather = None
    if "weather" in data:
        w = data["weather"]
        # Type-check temperature/humidity
        temperature = w.get("temperature", 0)
        humidity = w.get("humidity", 0)
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 0.0
        if isinstance(humidity, str):
            try:
                humidity = float(humidity)
            except (ValueError, TypeError):
                humidity = 0.0

        weather = WeatherData(
            location=w.get("location", ""),
            temperature=float(temperature),
            condition=WeatherCondition(w.get("condition", "sunny")),
            humidity=float(humidity),
        )

    ctx = TriggerContext(
        current_date=data.get("current_date", ""),
        weather=weather,
        user_actions=data.get("user_actions", []),
        user_preferences=data.get("user_preferences", {}),
        dismissed_widgets=set(data.get("dismissed_widgets", [])),
        developer_params=data.get("developer_params", {}),
    )

    # Load trigger rules from Firestore and build engine
    engine = TriggerEngine()
    rules = fb.get_trigger_rules()
    widgets = {w["id"]: w for w in fb.get_widgets()}

    for rule in rules:
        widget_id = rule.get("widget_id")
        if widget_id not in widgets:
            continue

        widget_data = widgets[widget_id]
        from server.models import WidgetCategory, WidgetContent, WidgetDefinition

        widget_def = WidgetDefinition(
            id=widget_id,
            name=widget_data.get("name", ""),
            category=WidgetCategory(widget_data.get("category", "informational")),
            content=WidgetContent(
                title=widget_data.get("params", {}).get("title", ""),
                actions=[],
            ),
            priority=widget_data.get("priority", 0),
        )

        conditions = build_conditions(rule.get("conditions", []))
        if conditions:
            engine.register(WidgetTriggerRule(
                widget=widget_def,
                conditions=conditions,
                match_mode=rule.get("match_mode", "all"),
            ))

    matched = engine.evaluate(ctx)

    # Return matched widgets with their full data from Firestore
    result = []
    for w in matched:
        widget_data = widgets.get(w.id)
        if widget_data:
            result.append(widget_data)

    # ── Track usage ──────────────────────────────────────────────────
    if license_key:
        user_id = data.get("user_id") or data.get("developer_params", {}).get("user_id")
        try:
            fb.increment_api_call(license_key, user_id if isinstance(user_id, str) else None)
        except Exception:
            pass  # Never fail a widget request due to tracking errors

    return jsonify({"widgets": result})


@widgets_bp.route("/<widget_id>/dismiss", methods=["POST"])
def dismiss_widget(widget_id: str):
    """Dismiss a widget for a user.
    ---
    tags:
      - Widgets
    summary: Dismiss widget
    description: Marks the widget as dismissed for the given user so it
      is excluded from future list and evaluate responses.
    security:
      - BearerAuth: []
    parameters:
      - name: widget_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
          properties:
            user_id:
              type: string
              example: user_abc123
    responses:
      200:
        description: Widget dismissed.
      400:
        description: user_id required.
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    fb.dismiss_widget(user_id, widget_id)
    return jsonify({"message": "Widget dismissed"})


@widgets_bp.route("/<widget_id>/interact", methods=["POST"])
def interact_widget(widget_id: str):
    """Record a widget interaction.
    ---
    tags:
      - Widgets
    summary: Record interaction
    description: Persists an interaction event (tap, expand, link_click, etc.)
      for analytics and trigger history.
    security:
      - BearerAuth: []
    parameters:
      - name: widget_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
          properties:
            user_id:
              type: string
              example: user_abc123
            action:
              type: string
              default: tap
              description: >
                Interaction type. Common values: tap, dismiss, expand,
                link_click, impression.
              example: tap
    responses:
      200:
        description: Interaction recorded.
      400:
        description: user_id required.
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    action = data.get("action", "tap")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    fb.record_interaction(user_id, widget_id, action)
    return jsonify({"message": "Interaction recorded"})


# --- User Action Endpoint (in widgets blueprint for simplicity) ---

@widgets_bp.route("/user/action", methods=["POST"])
def record_user_action():
    """Record a user action for trigger evaluation.
    ---
    tags:
      - Widgets
    summary: Record user action
    description: Stores an app-level behaviour event (page_view, purchase,
      signup, etc.) that the trigger engine can reference in conditions.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - action
          properties:
            user_id:
              type: string
              example: user_abc123
            action:
              type: string
              example: purchase_completed
            metadata:
              type: object
              description: Optional key/value pairs attached to the event.
              example:
                product_id: "prod_99"
                amount: 49.99
    responses:
      200:
        description: Action recorded.
      400:
        description: user_id and action required.
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    action = data.get("action")
    if not user_id or not action:
        return jsonify({"error": "user_id and action required"}), 400

    fb.record_user_action(user_id, action, data.get("metadata"))
    return jsonify({"message": "Action recorded"})
