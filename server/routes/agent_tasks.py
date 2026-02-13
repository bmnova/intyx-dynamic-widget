"""Agent task / persona management endpoints.

Developers define tasks like:
  "Benim appim bir kiyafet uygulamasi, kullaniciya hava durumuna gore
   oneri kombinler gosteren widget goster"

These tasks become the AI agent's persona/instructions when selecting
which widgets to show in the Flutter app.
"""

from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

agent_tasks_bp = Blueprint("agent_tasks", __name__, url_prefix="/api/agent-tasks")


def _get_tasks(api_key: str) -> list[dict]:
    """Get all tasks for an API key from cache."""
    doc = fb.get_cached_data(f"agent_tasks:{api_key}")
    if doc and isinstance(doc, dict):
        return doc.get("tasks", [])
    return []


def _save_tasks(api_key: str, tasks: list[dict]) -> None:
    """Save all tasks for an API key to cache."""
    fb.cache_data(f"agent_tasks:{api_key}", {"tasks": tasks})


@agent_tasks_bp.route("", methods=["POST"])
def create_task():
    """Create a new agent task / persona definition.

    Body: { "api_key": "...", "task": "...", "name": "..." }
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    task = data.get("task", "").strip()
    name = data.get("name", "").strip()

    if not api_key:
        return jsonify({"error": "api_key required"}), 400
    if not task:
        return jsonify({"error": "task description required"}), 400

    task_id = f"task_{uuid.uuid4().hex[:12]}"
    doc = {
        "id": task_id,
        "name": name or "Varsayilan Gorev",
        "task": task,
        "active": True,
    }

    tasks = _get_tasks(api_key)
    tasks.append(doc)
    _save_tasks(api_key, tasks)

    return jsonify({"id": task_id, "status": "created"}), 201


@agent_tasks_bp.route("", methods=["GET"])
def list_tasks():
    """List all agent tasks for an API key.

    Query: ?api_key=...
    """
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = _get_tasks(api_key)
    return jsonify({"tasks": tasks})


@agent_tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id: str):
    """Update an agent task."""
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = _get_tasks(api_key)
    found = False
    for t in tasks:
        if t["id"] == task_id:
            if "task" in data:
                t["task"] = data["task"]
            if "name" in data:
                t["name"] = data["name"]
            if "active" in data:
                t["active"] = data["active"]
            found = True
            break

    if not found:
        return jsonify({"error": "Task not found"}), 404

    _save_tasks(api_key, tasks)
    return jsonify({"status": "updated"})


@agent_tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id: str):
    """Delete an agent task."""
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = _get_tasks(api_key)
    new_tasks = [t for t in tasks if t["id"] != task_id]

    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404

    _save_tasks(api_key, new_tasks)
    return jsonify({"status": "deleted"})


@agent_tasks_bp.route("/resolve", methods=["POST"])
def resolve_task():
    """Resolve which widgets to show based on agent task + context.

    Body: { "api_key": "...", "task_id": "...", "context": { ... } }
    This calls the AI agent with the task persona + context.
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    task_id = data.get("task_id", "")
    context = data.get("context", {})

    if not api_key or not task_id:
        return jsonify({"error": "api_key and task_id required"}), 400

    tasks = _get_tasks(api_key)
    task_doc = next((t for t in tasks if t["id"] == task_id), None)
    if not task_doc:
        return jsonify({"error": "Task not found"}), 404

    enriched_context = {
        **context,
        "developer_task": task_doc["task"],
        "task_name": task_doc.get("name", ""),
    }

    from server.ai.gemini_client import get_gemini_client
    client = get_gemini_client()
    result = client.suggest_widgets(enriched_context)
    return jsonify(result)
