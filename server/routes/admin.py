"""Admin-only endpoints — requires INTYX_SERVER_API_KEY."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from server import firebase_client as fb
from server.config import SERVER_API_KEY

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_server_key():
    """Return 403 if the caller is not using the server API key."""
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else ""
    if not SERVER_API_KEY or token != SERVER_API_KEY:
        return jsonify({"error": "Forbidden — admin key required"}), 403
    return None


@admin_bp.route("/licenses", methods=["GET"])
def list_licenses():
    """List all licenses (admin only).
    ---
    tags:
      - Admin
    summary: List all licenses
    description: >
      Returns the most recent licenses. Requires the server API key in
      the Authorization header.
    parameters:
      - in: query
        name: limit
        type: integer
        default: 100
        description: Maximum number of records to return.
    responses:
      200:
        description: List of license records (api_key is masked).
      403:
        description: Missing or invalid server API key.
    """
    err = _require_server_key()
    if err:
        return err

    try:
        limit = min(int(request.args.get("limit", 100)), 500)
    except ValueError:
        limit = 100

    licenses = fb.list_licenses(limit=limit)
    return jsonify({"licenses": licenses, "count": len(licenses)})


@admin_bp.route("/stats", methods=["GET"])
def stats():
    """Basic platform stats (admin only).
    ---
    tags:
      - Admin
    summary: Platform statistics
    description: >
      Returns aggregate counts — total licenses by plan, total agent tasks,
      and total widgets. Requires the server API key.
    responses:
      200:
        description: Stats object.
      403:
        description: Missing or invalid server API key.
    """
    err = _require_server_key()
    if err:
        return err

    licenses = fb.list_licenses(limit=500)
    by_plan: dict[str, int] = {}
    active_count = 0
    for lic in licenses:
        plan = lic.get("plan", "unknown")
        by_plan[plan] = by_plan.get(plan, 0) + 1
        if lic.get("active"):
            active_count += 1

    return jsonify({
        "total_licenses": len(licenses),
        "active_licenses": active_count,
        "by_plan": by_plan,
    })
