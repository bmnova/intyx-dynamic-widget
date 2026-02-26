"""Paddle payment webhook handler.

Paddle sends a POST to /api/paddle/webhook when a checkout completes.
We verify the signature and create a license key automatically.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid

from flask import Blueprint, jsonify, request

from server import firebase_client as fb
from server.config import PADDLE_WEBHOOK_SECRET

logger = logging.getLogger(__name__)

paddle_bp = Blueprint("paddle", __name__, url_prefix="/api/paddle")

PLAN_MAP = {
    # Sandbox price IDs → plan names
    "pri_01kjcjsbqvqbns6q2p04maddea": "pro",
}

# Map Paddle product IDs to plan names (fallback when price ID not in PLAN_MAP)
PRODUCT_MAP = {
    "pro_01kjb1xhk5gtq4tm6m9a5g6x14": "pro",
}


def _verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Paddle webhook HMAC-SHA256 signature."""
    if not PADDLE_WEBHOOK_SECRET:
        logger.warning("PADDLE_WEBHOOK_SECRET not set — skipping signature verification")
        return True

    # Paddle sends: ts=<timestamp>;h1=<hash>
    parts = {}
    for segment in signature.split(";"):
        if "=" in segment:
            k, v = segment.split("=", 1)
            parts[k] = v

    ts = parts.get("ts", "")
    h1 = parts.get("h1", "")
    if not ts or not h1:
        return False

    signed_payload = f"{ts}:{payload.decode('utf-8')}"
    expected = hmac.new(
        PADDLE_WEBHOOK_SECRET.encode(),
        signed_payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, h1)


@paddle_bp.route("/webhook", methods=["POST"])
def paddle_webhook():
    """Handle Paddle webhook events (checkout.completed, subscription.*, etc.)."""
    raw_body = request.get_data()
    signature = request.headers.get("Paddle-Signature", "")

    if not _verify_signature(raw_body, signature):
        logger.warning("Paddle webhook signature verification failed")
        return jsonify({"error": "Invalid signature"}), 403

    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    event_type = event.get("event_type", "")
    data = event.get("data", {})

    logger.info("Paddle event: %s", event_type)

    if event_type == "transaction.completed":
        return _handle_transaction_completed(data)

    if event_type == "subscription.canceled":
        return _handle_subscription_canceled(data)

    # Acknowledge unknown events
    return jsonify({"status": "ignored", "event_type": event_type})


def _handle_transaction_completed(data: dict) -> tuple:
    """Create a license key when payment succeeds."""
    customer_email = data.get("customer", {}).get("email", "")
    items = data.get("items", [])

    # Determine plan from price ID, then product ID, then product name
    plan = "starter"
    for item in items:
        price_id = item.get("price", {}).get("id", "")
        if price_id in PLAN_MAP:
            plan = PLAN_MAP[price_id]
            break
        product_id = item.get("product", {}).get("id", "")
        if product_id in PRODUCT_MAP:
            plan = PRODUCT_MAP[product_id]
            break
        # Fallback: check product name
        product_name = item.get("product", {}).get("name", "").lower()
        if "enterprise" in product_name:
            plan = "enterprise"
        elif "pro" in product_name:
            plan = "pro"

    api_key = f"intyx_{plan}_{uuid.uuid4().hex[:16]}"

    license_doc = {
        "api_key": api_key,
        "plan": plan,
        "email": customer_email,
        "active": True,
        "widget_limit": {"starter": 3, "pro": 10, "enterprise": -1}[plan],
        "mau_limit": {"starter": 1000, "pro": 50000, "enterprise": -1}[plan],
        "paddle_transaction_id": data.get("id", ""),
        "paddle_customer_id": data.get("customer_id", ""),
    }

    # Persist to Firestore (not just cache)
    fb.create_license(api_key, license_doc)

    logger.info("License created: plan=%s email=%s", plan, customer_email)
    return jsonify({"status": "license_created", "plan": plan}), 200


def _handle_subscription_canceled(data: dict) -> tuple:
    """Deactivate license when subscription is canceled."""
    customer_id = data.get("customer_id", "")
    if not customer_id:
        return jsonify({"status": "no_customer_id"}), 200

    # Find and deactivate the license
    deactivated = fb.deactivate_license_by_paddle_customer(customer_id)
    logger.info("Subscription canceled: customer=%s deactivated=%s", customer_id, deactivated)
    return jsonify({"status": "deactivated" if deactivated else "not_found"}), 200
