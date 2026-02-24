"""Firebase Firestore client for the Dynamic Widget System."""

from __future__ import annotations

import threading
import time
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

from server.config import FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID


_db = None
_db_lock = threading.Lock()


def init_firebase() -> None:
    """Initialize Firebase Admin SDK (thread-safe with double-check locking)."""
    global _db
    if _db is not None:
        return

    with _db_lock:
        # Double-check after acquiring lock
        if _db is not None:
            return

        cred = None
        if FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

        firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID})
        _db = firestore.client()


def get_db() -> firestore.Client:
    """Return the Firestore client, initializing if needed."""
    if _db is None:
        init_firebase()
    return _db


# --- Widget Operations ---


def get_widgets(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Fetch widget definitions from Firestore with pagination."""
    db = get_db()
    query = db.collection("widgets")
    if offset > 0:
        query = query.offset(offset)
    query = query.limit(limit)
    docs = query.stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]


def get_widget(widget_id: str) -> dict[str, Any] | None:
    """Fetch a single widget definition."""
    db = get_db()
    doc = db.collection("widgets").document(widget_id).get()
    if doc.exists:
        return {**doc.to_dict(), "id": doc.id}
    return None


def create_widget(data: dict[str, Any]) -> str:
    """Create a new widget definition. Returns the document ID."""
    db = get_db()
    data["created_at"] = time.time()
    doc_ref = db.collection("widgets").add(data)
    return doc_ref[1].id


def update_widget(widget_id: str, data: dict[str, Any]) -> bool:
    """Update an existing widget definition."""
    db = get_db()
    doc_ref = db.collection("widgets").document(widget_id)
    if not doc_ref.get().exists:
        return False
    data["updated_at"] = time.time()
    doc_ref.update(data)
    return True


def delete_widget(widget_id: str) -> bool:
    """Delete a widget definition."""
    db = get_db()
    doc_ref = db.collection("widgets").document(widget_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


# --- Trigger Rule Operations ---


def get_trigger_rules(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
    """Fetch trigger rules from Firestore with pagination."""
    db = get_db()
    query = db.collection("trigger_rules")
    if offset > 0:
        query = query.offset(offset)
    query = query.limit(limit)
    docs = query.stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]


def create_trigger_rule(data: dict[str, Any]) -> str:
    """Create a new trigger rule."""
    db = get_db()
    data["created_at"] = time.time()
    doc_ref = db.collection("trigger_rules").add(data)
    return doc_ref[1].id


def delete_trigger_rule(rule_id: str) -> bool:
    """Delete a trigger rule."""
    db = get_db()
    doc_ref = db.collection("trigger_rules").document(rule_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True


# --- User State Operations ---


def get_user_state(user_id: str) -> dict[str, Any]:
    """Get user state (dismissed widgets, interactions, user actions)."""
    db = get_db()
    doc = db.collection("user_states").document(user_id).get()
    if doc.exists:
        return doc.to_dict()
    return {"dismissed_widgets": [], "interactions": [], "user_actions": []}


def dismiss_widget(user_id: str, widget_id: str) -> None:
    """Record that a user dismissed a widget (transactional)."""
    db = get_db()
    doc_ref = db.collection("user_states").document(user_id)

    @firestore.transactional
    def _dismiss(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            state = snapshot.to_dict()
            dismissed = state.get("dismissed_widgets", [])
            if widget_id not in dismissed:
                dismissed.append(widget_id)
                transaction.update(doc_ref, {"dismissed_widgets": dismissed})
        else:
            transaction.set(doc_ref, {
                "dismissed_widgets": [widget_id],
                "interactions": [],
                "user_actions": [],
            })

    _dismiss(db.transaction())


def record_interaction(user_id: str, widget_id: str, action: str) -> None:
    """Record a user interaction with a widget (transactional).

    Interactions are widget-specific events (tap, dismiss, expand, etc.)
    stored in a separate 'interactions' array.
    """
    db = get_db()
    doc_ref = db.collection("user_states").document(user_id)

    interaction = {
        "widget_id": widget_id,
        "action": action,
        "timestamp": time.time(),
    }

    @firestore.transactional
    def _record(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            state = snapshot.to_dict()
            interactions = state.get("interactions", [])
            interactions.append(interaction)
            transaction.update(doc_ref, {"interactions": interactions})
        else:
            transaction.set(doc_ref, {
                "dismissed_widgets": [],
                "interactions": [interaction],
                "user_actions": [],
            })

    _record(db.transaction())


def record_user_action(user_id: str, action: str, metadata: dict[str, Any] | None = None) -> None:
    """Record a generic user action for trigger evaluation (transactional).

    User actions are app-level behaviour events (page_view, purchase, signup)
    used by the trigger engine. Stored in a separate 'user_actions' array.
    """
    db = get_db()
    doc_ref = db.collection("user_states").document(user_id)

    entry = {"action": action, "timestamp": time.time()}
    if metadata:
        entry["metadata"] = metadata

    @firestore.transactional
    def _record(transaction):
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            state = snapshot.to_dict()
            user_actions = state.get("user_actions", [])
            user_actions.append(entry)
            transaction.update(doc_ref, {"user_actions": user_actions})
        else:
            transaction.set(doc_ref, {
                "dismissed_widgets": [],
                "interactions": [],
                "user_actions": [entry],
            })

    _record(db.transaction())


# --- Data Cache Operations ---


def cache_data(source: str, data: dict[str, Any]) -> None:
    """Cache data source results in Firestore."""
    db = get_db()
    db.collection("data_cache").document(source).set({
        "data": data,
        "updated_at": time.time(),
    })


def get_cached_data(source: str) -> dict[str, Any] | None:
    """Get cached data source results."""
    db = get_db()
    doc = db.collection("data_cache").document(source).get()
    if doc.exists:
        return doc.to_dict().get("data")
    return None


def delete_cached_data(source: str) -> None:
    """Delete a cached data entry."""
    db = get_db()
    db.collection("data_cache").document(source).delete()


# --- License Operations (Firestore-backed) ---


def create_license(api_key: str, data: dict[str, Any]) -> None:
    """Persist a license in both Firestore and data_cache for fast lookups."""
    db = get_db()
    data["created_at"] = time.time()
    db.collection("licenses").document(api_key).set(data)
    cache_data(f"license:{api_key}", data)


def get_license(api_key: str) -> dict[str, Any] | None:
    """Get a license — try cache first, then Firestore."""
    cached = get_cached_data(f"license:{api_key}")
    if cached:
        return cached
    db = get_db()
    doc = db.collection("licenses").document(api_key).get()
    if doc.exists:
        data = doc.to_dict()
        cache_data(f"license:{api_key}", data)
        return data
    return None


def deactivate_license_by_paddle_customer(customer_id: str) -> bool:
    """Deactivate all licenses for a Paddle customer ID."""
    db = get_db()
    docs = db.collection("licenses").where("paddle_customer_id", "==", customer_id).stream()
    found = False
    for doc in docs:
        doc.reference.update({"active": False, "deactivated_at": time.time()})
        api_key = doc.to_dict().get("api_key", doc.id)
        cache_data(f"license:{api_key}", {**doc.to_dict(), "active": False})
        found = True
    return found


def count_widgets_for_license(api_key: str) -> int:
    """Count widgets created by a specific license key."""
    db = get_db()
    docs = db.collection("widgets").where("license_key", "==", api_key).stream()
    return sum(1 for _ in docs)


def list_licenses(limit: int = 100) -> list[dict]:
    """Return the most recent licenses ordered by creation time (admin use only)."""
    db = get_db()
    docs = (
        db.collection("licenses")
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        # Never expose the raw api_key in the listing — mask it
        raw_key = data.get("api_key", doc.id)
        data["api_key_masked"] = raw_key[:12] + "…" if len(raw_key) > 12 else raw_key
        data.pop("api_key", None)
        result.append(data)
    return result


# --- Agent Task Operations (Firestore-backed) ---


def get_agent_tasks(api_key: str) -> list[dict[str, Any]]:
    """Get agent tasks — try cache first, then Firestore."""
    cached = get_cached_data(f"agent_tasks:{api_key}")
    if cached and isinstance(cached, dict):
        return cached.get("tasks", [])
    db = get_db()
    doc = db.collection("agent_tasks").document(api_key).get()
    if doc.exists:
        data = doc.to_dict()
        tasks = data.get("tasks", [])
        cache_data(f"agent_tasks:{api_key}", {"tasks": tasks})
        return tasks
    return []


def save_agent_tasks(api_key: str, tasks: list[dict[str, Any]]) -> None:
    """Persist agent tasks to both Firestore and cache."""
    db = get_db()
    payload = {"tasks": tasks, "updated_at": time.time()}
    db.collection("agent_tasks").document(api_key).set(payload)
    cache_data(f"agent_tasks:{api_key}", payload)
