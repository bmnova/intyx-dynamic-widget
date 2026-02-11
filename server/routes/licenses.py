"""License key management endpoints."""

from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

licenses_bp = Blueprint("licenses", __name__, url_prefix="/api/licenses")


@licenses_bp.route("", methods=["POST"])
def create_license():
    """Create a new license key after successful purchase.

    Expected body: { "plan": "starter|pro|enterprise", "email": "..." }
    In production this would be called by the Paddle webhook.
    """
    data = request.get_json() or {}
    plan = data.get("plan")
    email = data.get("email", "")

    if plan not in ("starter", "pro", "enterprise"):
        return jsonify({"error": "Invalid plan"}), 400

    api_key = f"intyx_{plan}_{uuid.uuid4().hex[:16]}"

    doc = {
        "api_key": api_key,
        "plan": plan,
        "email": email,
        "active": True,
        "widget_limit": {"starter": 3, "pro": 10, "enterprise": -1}[plan],
        "mau_limit": {"starter": 1000, "pro": 50000, "enterprise": -1}[plan],
    }
    fb.cache_data(f"license:{api_key}", doc)

    return jsonify({"api_key": api_key, "plan": plan}), 201


@licenses_bp.route("/validate", methods=["POST"])
def validate_license():
    """Validate a license key — called by the Flutter SDK on init.

    Expected body: { "api_key": "intyx_..." }
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")

    if not api_key.startswith("intyx_"):
        return jsonify({"valid": False, "error": "Invalid key format"}), 401

    doc = fb.get_cached_data(f"license:{api_key}")
    if not doc or not doc.get("active"):
        return jsonify({"valid": False, "error": "Key not found or inactive"}), 401

    return jsonify({
        "valid": True,
        "plan": doc["plan"],
        "widget_limit": doc["widget_limit"],
        "mau_limit": doc["mau_limit"],
    })
