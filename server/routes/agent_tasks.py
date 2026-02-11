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
        "api_key": api_key,
        "name": name or "Varsayilan Gorev",
        "task": task,
        "active": True,
    }
    fb.cache_data(f"agent_task:{api_key}:{task_id}", doc)

    return jsonify({"id": task_id, "status": "created"}), 201


@agent_tasks_bp.route("", methods=["GET"])
def list_tasks():
    """List all agent tasks for an API key.

    Query: ?api_key=...
    """
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    # Fetch all tasks for this key
    tasks = fb.get_cached_data(f"agent_tasks_list:{api_key}") or {"tasks": []}
    return jsonify(tasks)


@agent_tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id: str):
    """Update an agent task."""
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    existing = fb.get_cached_data(f"agent_task:{api_key}:{task_id}")
    if not existing:
        return jsonify({"error": "Task not found"}), 404

    if "task" in data:
        existing["task"] = data["task"]
    if "name" in data:
        existing["name"] = data["name"]
    if "active" in data:
        existing["active"] = data["active"]

    fb.cache_data(f"agent_task:{api_key}:{task_id}", existing)
    return jsonify({"status": "updated"})


@agent_tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id: str):
    """Delete an agent task."""
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    fb.cache_data(f"agent_task:{api_key}:{task_id}", None)
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

    task_doc = fb.get_cached_data(f"agent_task:{api_key}:{task_id}")
    if not task_doc:
        return jsonify({"error": "Task not found"}), 404

    # Inject the developer's task description into the AI context
    enriched_context = {
        **context,
        "developer_task": task_doc["task"],
        "task_name": task_doc.get("name", ""),
    }

    from server.ai.gemini_client import GeminiClient
    client = GeminiClient()
    result = client.suggest_widgets(enriched_context)
    return jsonify(result)
