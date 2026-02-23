"""Widget API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb
from server.ai.gemini_client import VALID_WIDGET_TYPES
from server.models import ColorPalette, TriggerContext, WeatherCondition, WeatherData
from server.triggers.conditions import build_conditions
from server.triggers.engine import TriggerEngine, WidgetTriggerRule

widgets_bp = Blueprint("widgets", __name__, url_prefix="/api/widgets")


@widgets_bp.route("", methods=["GET"])
def list_widgets():
    """List all active widgets, optionally filtered by user context.

    Query params:
        user_id: Filter out dismissed widgets for this user
        limit: Max widgets to return (default 100)
        offset: Skip N widgets for pagination (default 0)
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
    """Get a single widget definition."""
    widget = fb.get_widget(widget_id)
    if not widget:
        return jsonify({"error": "Widget not found"}), 404
    return jsonify(widget)


@widgets_bp.route("", methods=["POST"])
def create_widget():
    """Create a new widget definition."""
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
    """Update an existing widget."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    if fb.update_widget(widget_id, data):
        return jsonify({"message": "Widget updated"})
    return jsonify({"error": "Widget not found"}), 404


@widgets_bp.route("/<widget_id>", methods=["DELETE"])
def delete_widget(widget_id: str):
    """Delete a widget."""
    if fb.delete_widget(widget_id):
        return jsonify({"message": "Widget deleted"})
    return jsonify({"error": "Widget not found"}), 404


@widgets_bp.route("/evaluate", methods=["POST"])
def evaluate_triggers():
    """Evaluate trigger rules against provided context and return matching widgets."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Context required"}), 400

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

    return jsonify({"widgets": result})


@widgets_bp.route("/<widget_id>/dismiss", methods=["POST"])
def dismiss_widget(widget_id: str):
    """Dismiss a widget for a user."""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    fb.dismiss_widget(user_id, widget_id)
    return jsonify({"message": "Widget dismissed"})


@widgets_bp.route("/<widget_id>/interact", methods=["POST"])
def interact_widget(widget_id: str):
    """Record a widget interaction."""
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
    """Record a user action for trigger evaluation."""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    action = data.get("action")
    if not user_id or not action:
        return jsonify({"error": "user_id and action required"}), 400

    fb.record_user_action(user_id, action, data.get("metadata"))
    return jsonify({"message": "Action recorded"})
