"""Agent task / persona management endpoints.

Developers define tasks like:
  "My app is a fashion app; show a widget that suggests outfit
   combinations based on the weather"

These tasks become the AI agent's persona/instructions when selecting
which widgets to show in the Flutter app.

Data is now persisted in Firestore (not just in-memory cache).
"""

from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, request

from server import firebase_client as fb

agent_tasks_bp = Blueprint("agent_tasks", __name__, url_prefix="/api/agent-tasks")


@agent_tasks_bp.route("", methods=["POST"])
def create_task():
    """Create a new agent task / persona definition.
    ---
    tags:
      - Agent Tasks
    summary: Create agent task
    description: >
      An agent task is a natural-language description of your app's context
      and goals. The AI uses it as a persona when deciding which widgets to
      surface. Stored in Firestore under your API key.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - api_key
            - task
          properties:
            api_key:
              type: string
              example: intyx_pro_a1b2c3d4e5f6g7h8
            task:
              type: string
              description: Natural-language description of your app's widget goal.
              example: >
                My app is a fitness tracker. Show motivational widgets when
                the user hasn't logged a workout in 3 days.
            name:
              type: string
              description: Human-readable label for this task.
              example: Re-engagement nudge
    responses:
      201:
        description: Task created.
        schema:
          type: object
          properties:
            id:
              type: string
              example: task_a1b2c3d4e5f6
            status:
              type: string
              example: created
      400:
        description: api_key or task missing.
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
        "name": name or "Default Task",
        "task": task,
        "active": True,
    }

    tasks = fb.get_agent_tasks(api_key)
    tasks.append(doc)
    fb.save_agent_tasks(api_key, tasks)

    return jsonify({"id": task_id, "status": "created"}), 201


@agent_tasks_bp.route("", methods=["GET"])
def list_tasks():
    """List all agent tasks for an API key.
    ---
    tags:
      - Agent Tasks
    summary: List agent tasks
    security:
      - BearerAuth: []
    parameters:
      - name: api_key
        in: query
        type: string
        required: true
        example: intyx_pro_a1b2c3d4e5f6g7h8
    responses:
      200:
        description: List of tasks.
        schema:
          type: object
          properties:
            tasks:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  task:
                    type: string
                  active:
                    type: boolean
      400:
        description: api_key required.
    """
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = fb.get_agent_tasks(api_key)
    return jsonify({"tasks": tasks})


@agent_tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id: str):
    """Update an agent task.
    ---
    tags:
      - Agent Tasks
    summary: Update agent task
    security:
      - BearerAuth: []
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
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
              example: intyx_pro_a1b2c3d4e5f6g7h8
            task:
              type: string
            name:
              type: string
            active:
              type: boolean
    responses:
      200:
        description: Task updated.
      404:
        description: Task not found.
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = fb.get_agent_tasks(api_key)
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

    fb.save_agent_tasks(api_key, tasks)
    return jsonify({"status": "updated"})


@agent_tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id: str):
    """Delete an agent task.
    ---
    tags:
      - Agent Tasks
    summary: Delete agent task
    security:
      - BearerAuth: []
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
      - name: api_key
        in: query
        type: string
        required: true
    responses:
      200:
        description: Task deleted.
      404:
        description: Task not found.
    """
    api_key = request.args.get("api_key", "")
    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    tasks = fb.get_agent_tasks(api_key)
    new_tasks = [t for t in tasks if t["id"] != task_id]

    if len(new_tasks) == len(tasks):
        return jsonify({"error": "Task not found"}), 404

    fb.save_agent_tasks(api_key, new_tasks)
    return jsonify({"status": "deleted"})


@agent_tasks_bp.route("/resolve", methods=["POST"])
def resolve_task():
    """Resolve widgets for a specific agent task and context.
    ---
    tags:
      - Agent Tasks
    summary: Resolve task widgets
    description: >
      Fetches the task definition, injects it into the AI context as a
      persona, then calls the AI suggest endpoint. Returns the widgets
      the AI recommends for the given task + user context combination.
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - api_key
            - task_id
          properties:
            api_key:
              type: string
              example: intyx_pro_a1b2c3d4e5f6g7h8
            task_id:
              type: string
              example: task_a1b2c3d4e5f6
            context:
              type: object
              description: Current user/app context passed to the AI.
              example:
                current_screen: home
                user_segment: power_user
    responses:
      200:
        description: AI-suggested widgets for the task.
        schema:
          type: object
          properties:
            widgets:
              type: array
              items:
                type: object
      400:
        description: api_key and task_id required.
      404:
        description: Task not found.
    """
    data = request.get_json() or {}
    api_key = data.get("api_key", "")
    task_id = data.get("task_id", "")
    context = data.get("context", {})

    if not api_key or not task_id:
        return jsonify({"error": "api_key and task_id required"}), 400

    tasks = fb.get_agent_tasks(api_key)
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
