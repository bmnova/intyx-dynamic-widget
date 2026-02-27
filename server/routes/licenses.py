"""License key management endpoints."""

from __future__ import annotations

import uuid
from datetime import date

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

licenses_bp = Blueprint("licenses", __name__, url_prefix="/api/licenses")


@licenses_bp.route("", methods=["POST"])
def create_license():
    """Create a new license key after successful purchase.
    ---
    tags:
      - Licenses
    summary: Create license key
    description: >
      Generates an `intyx_*` API key for a given plan. In production this
      endpoint is called by the Paddle webhook — not directly by clients.
      It is listed as a public path so no auth header is required.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - plan
          properties:
            plan:
              type: string
              enum: [starter, pro, enterprise]
              example: pro
            email:
              type: string
              format: email
              example: user@example.com
    responses:
      201:
        description: License created.
        schema:
          type: object
          properties:
            api_key:
              type: string
              example: intyx_pro_a1b2c3d4e5f6g7h8
            plan:
              type: string
              example: pro
      400:
        description: Invalid plan.
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
    fb.create_license(api_key, doc)

    return jsonify({"api_key": api_key, "plan": plan}), 201


@licenses_bp.route("/validate", methods=["POST"])
def validate_license():
    """Validate a license key.
    ---
    tags:
      - Licenses
    summary: Validate license
    description: >
      Called by the Flutter SDK on `IntyxDynamicWidget.init()` to confirm
      the API key is active and retrieve plan details. This endpoint is
      public (no auth header required).
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - api_key
          properties:
            api_key:
              type: string
              description: License key starting with `intyx_`.
              example: intyx_pro_a1b2c3d4e5f6g7h8
    responses:
      200:
        description: License is valid.
        schema:
          type: object
          properties:
            valid:
              type: boolean
              example: true
            plan:
              type: string
              example: pro
            widget_limit:
              type: integer
              description: Max widgets allowed (-1 = unlimited).
              example: 10
            mau_limit:
              type: integer
              description: Max monthly active users (-1 = unlimited).
              example: 50000
      401:
        description: Invalid or inactive license key.
        schema:
          type: object
          properties:
            valid:
              type: boolean
              example: false
            error:
              type: string
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")

    if not api_key.startswith("intyx_"):
        return jsonify({"valid": False, "error": "Invalid key format"}), 401

    doc = fb.get_license(api_key)
    if not doc or not doc.get("active"):
        return jsonify({"valid": False, "error": "Key not found or inactive"}), 401

    return jsonify({
        "valid": True,
        "plan": doc["plan"],
        "widget_limit": doc["widget_limit"],
        "mau_limit": doc["mau_limit"],
    })


@licenses_bp.route("/usage", methods=["GET"])
def get_license_usage():
    """Return current-month usage statistics for the authenticated license key.
    ---
    tags:
      - Licenses
    summary: Get license usage
    description: >
      Returns API call counts and Monthly Active Users (MAU) for the
      current calendar month, along with plan limits and the reset date.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Usage statistics.
        schema:
          type: object
          properties:
            plan:
              type: string
              example: starter
            api_calls:
              type: object
              properties:
                used:
                  type: integer
                limit:
                  type: integer
                  description: -1 means unlimited.
            mau:
              type: object
              properties:
                used:
                  type: integer
                limit:
                  type: integer
                  description: -1 means unlimited.
                percent:
                  type: integer
            resets_at:
              type: string
              format: date
              example: "2026-03-01"
      401:
        description: Valid license key required.
    """
    auth = request.headers.get("Authorization", "")
    api_key = auth[7:] if auth.startswith("Bearer ") else request.args.get("api_key", "")

    if not api_key.startswith("intyx_"):
        return jsonify({"error": "Valid license key required"}), 401

    lic = fb.get_license(api_key)
    if not lic or not lic.get("active"):
        return jsonify({"error": "License not found or inactive"}), 401

    usage = fb.get_usage(api_key)
    mau_limit = lic.get("mau_limit", -1)
    mau_used = len(usage.get("unique_users", []))
    api_calls_used = usage.get("api_calls", 0)

    # First day of next month = reset date
    today = date.today()
    if today.month == 12:
        resets_at = date(today.year + 1, 1, 1)
    else:
        resets_at = date(today.year, today.month + 1, 1)

    def _pct(used: int, limit: int) -> int:
        if limit <= 0:
            return 0
        return min(round(used * 100 / limit), 100)

    return jsonify({
        "plan": lic.get("plan"),
        "api_calls": {
            "used": api_calls_used,
            "limit": -1,  # No hard cap on evaluate calls; MAU is the enforced limit
        },
        "mau": {
            "used": mau_used,
            "limit": mau_limit,
            "percent": _pct(mau_used, mau_limit),
        },
        "resets_at": resets_at.isoformat(),
    })
