"""Email signup endpoints for live event notifications."""

from __future__ import annotations

import re

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

email_signup_bp = Blueprint("email_signup", __name__, url_prefix="/api/email-signup")

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@email_signup_bp.route("", methods=["POST"])
def subscribe():
    """Subscribe an email to live event notifications.
    ---
    tags:
      - Email Signup
    summary: Subscribe to live event notifications
    description: Registers an email address to receive a notification when a
      live event starts. Duplicate emails are silently accepted (idempotent).
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            source:
              type: string
              default: live_event
              description: Notification source/channel identifier.
    responses:
      200:
        description: Email registered (or already registered).
        schema:
          type: object
          properties:
            message:
              type: string
            already_registered:
              type: boolean
      400:
        description: Invalid or missing email.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    email = (data.get("email") or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        return jsonify({"error": "Valid email address required"}), 400

    source = data.get("source", "live_event")
    is_new = fb.add_email_signup(email, source)

    if is_new:
        return jsonify({"message": "Successfully subscribed!", "already_registered": False})
    return jsonify({"message": "You are already subscribed.", "already_registered": True})


@email_signup_bp.route("/count", methods=["GET"])
def subscriber_count():
    """Get the number of subscribers for a source.
    ---
    tags:
      - Email Signup
    summary: Get subscriber count
    security:
      - BearerAuth: []
    parameters:
      - name: source
        in: query
        type: string
        required: false
        default: live_event
    responses:
      200:
        description: Subscriber count.
        schema:
          type: object
          properties:
            count:
              type: integer
            source:
              type: string
    """
    source = request.args.get("source", "live_event")
    count = fb.count_email_signups(source)
    return jsonify({"count": count, "source": source})


@email_signup_bp.route("/list", methods=["GET"])
def list_subscribers():
    """List all subscribers (admin only).
    ---
    tags:
      - Email Signup
    summary: List subscribers
    security:
      - BearerAuth: []
    parameters:
      - name: source
        in: query
        type: string
        required: false
        default: live_event
      - name: limit
        in: query
        type: integer
        required: false
        default: 500
    responses:
      200:
        description: Subscriber list.
        schema:
          type: object
          properties:
            subscribers:
              type: array
              items:
                type: object
            count:
              type: integer
    """
    source = request.args.get("source", "live_event")
    limit = min(int(request.args.get("limit", 500)), 1000)
    subscribers = fb.get_email_signups(source, limit)
    return jsonify({"subscribers": subscribers, "count": len(subscribers)})
