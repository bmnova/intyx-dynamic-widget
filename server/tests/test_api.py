"""Tests for Flask API endpoints."""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock external dependencies that may not be installed in test env
for mod in [
    "firebase_admin", "firebase_admin.credentials", "firebase_admin.firestore",
    "google.generativeai", "mcp", "mcp.server", "mcp.server.stdio", "mcp.types",
    "sentry_sdk", "sentry_sdk.integrations.flask",
]:
    sys.modules.setdefault(mod, MagicMock())

# Set required env vars before importing app
import os
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")

from server.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ok"


class TestWidgetEndpoints:
    @patch("server.routes.widgets.fb")
    def test_list_widgets(self, mock_fb, client):
        mock_fb.get_widgets.return_value = [
            {"id": "w1", "type": "informational", "params": {"title": "Test"}, "priority": 0}
        ]
        resp = client.get("/api/widgets")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data["widgets"]) == 1

    @patch("server.routes.widgets.fb")
    def test_list_widgets_with_user_filter(self, mock_fb, client):
        mock_fb.get_widgets.return_value = [
            {"id": "w1", "type": "informational", "params": {}, "priority": 0},
            {"id": "w2", "type": "promotional", "params": {}, "priority": 0},
        ]
        mock_fb.get_user_state.return_value = {"dismissed_widgets": ["w1"], "actions": []}

        resp = client.get("/api/widgets?user_id=user1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data["widgets"]) == 1
        assert data["widgets"][0]["id"] == "w2"

    @patch("server.routes.widgets.fb")
    def test_get_widget(self, mock_fb, client):
        mock_fb.get_widget.return_value = {"id": "w1", "type": "informational", "params": {}}
        resp = client.get("/api/widgets/w1")
        assert resp.status_code == 200

    @patch("server.routes.widgets.fb")
    def test_get_widget_not_found(self, mock_fb, client):
        mock_fb.get_widget.return_value = None
        resp = client.get("/api/widgets/nonexistent")
        assert resp.status_code == 404

    @patch("server.routes.widgets.fb")
    def test_create_widget(self, mock_fb, client):
        mock_fb.create_widget.return_value = "new_id"
        resp = client.post(
            "/api/widgets",
            data=json.dumps({"type": "informational", "params": {"title": "Test"}}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["id"] == "new_id"

    @patch("server.routes.widgets.fb")
    def test_create_widget_missing_fields(self, mock_fb, client):
        resp = client.post(
            "/api/widgets",
            data=json.dumps({"name": "incomplete"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    @patch("server.routes.widgets.fb")
    def test_dismiss_widget(self, mock_fb, client):
        resp = client.post(
            "/api/widgets/w1/dismiss",
            data=json.dumps({"user_id": "user1"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        mock_fb.dismiss_widget.assert_called_once_with("user1", "w1")

    @patch("server.routes.widgets.fb")
    def test_dismiss_widget_no_user(self, mock_fb, client):
        resp = client.post(
            "/api/widgets/w1/dismiss",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    @patch("server.routes.widgets.fb")
    def test_interact_widget(self, mock_fb, client):
        resp = client.post(
            "/api/widgets/w1/interact",
            data=json.dumps({"user_id": "user1", "action": "click"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        mock_fb.record_interaction.assert_called_once_with("user1", "w1", "click")

    @patch("server.routes.widgets.fb")
    def test_record_user_action(self, mock_fb, client):
        resp = client.post(
            "/api/widgets/user/action",
            data=json.dumps({"user_id": "user1", "action": "purchase"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        mock_fb.record_user_action.assert_called_once()


class TestLicenseEndpoints:
    @patch("server.routes.licenses.fb")
    def test_create_license(self, mock_fb, client):
        resp = client.post(
            "/api/licenses",
            data=json.dumps({"plan": "pro", "email": "test@example.com"}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["plan"] == "pro"
        assert data["api_key"].startswith("intyx_pro_")
        mock_fb.create_license.assert_called_once()

    def test_create_license_invalid_plan(self, client):
        resp = client.post(
            "/api/licenses",
            data=json.dumps({"plan": "invalid"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    @patch("server.routes.licenses.fb")
    def test_validate_license_success(self, mock_fb, client):
        mock_fb.get_license.return_value = {
            "active": True,
            "plan": "pro",
            "widget_limit": 10,
            "mau_limit": 50000,
        }
        resp = client.post(
            "/api/licenses/validate",
            data=json.dumps({"api_key": "intyx_pro_abc123"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["valid"] is True
        assert data["plan"] == "pro"

    @patch("server.routes.licenses.fb")
    def test_validate_license_invalid(self, mock_fb, client):
        mock_fb.get_license.return_value = None
        resp = client.post(
            "/api/licenses/validate",
            data=json.dumps({"api_key": "intyx_pro_invalid"}),
            content_type="application/json",
        )
        assert resp.status_code == 401


class TestAgentTaskEndpoints:
    @patch("server.routes.agent_tasks.fb")
    def test_create_task(self, mock_fb, client):
        mock_fb.get_agent_tasks.return_value = []
        resp = client.post(
            "/api/agent-tasks",
            data=json.dumps({
                "api_key": "intyx_pro_abc",
                "task": "Fashion app weather suggestions",
                "name": "Weather Outfits",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["status"] == "created"
        assert data["id"].startswith("task_")
        mock_fb.save_agent_tasks.assert_called_once()

    @patch("server.routes.agent_tasks.fb")
    def test_list_tasks(self, mock_fb, client):
        mock_fb.get_agent_tasks.return_value = [
            {"id": "task_1", "name": "Test", "task": "test", "active": True},
        ]
        resp = client.get("/api/agent-tasks?api_key=intyx_pro_abc")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data["tasks"]) == 1

    def test_list_tasks_no_key(self, client):
        resp = client.get("/api/agent-tasks")
        assert resp.status_code == 400

    @patch("server.routes.agent_tasks.fb")
    def test_delete_task(self, mock_fb, client):
        mock_fb.get_agent_tasks.return_value = [
            {"id": "task_1", "name": "Test", "task": "test", "active": True},
        ]
        resp = client.delete("/api/agent-tasks/task_1?api_key=intyx_pro_abc")
        assert resp.status_code == 200
        mock_fb.save_agent_tasks.assert_called_once()


class TestPaddleWebhook:
    def test_webhook_invalid_json(self, client):
        resp = client.post(
            "/api/paddle/webhook",
            data=b"not json",
            content_type="application/json",
        )
        assert resp.status_code == 400

    @patch("server.routes.paddle_webhook.fb")
    def test_webhook_transaction_completed(self, mock_fb, client):
        event = {
            "event_type": "transaction.completed",
            "data": {
                "id": "txn_123",
                "customer": {"email": "user@example.com"},
                "items": [{"product": {"name": "Pro Plan"}}],
            },
        }
        resp = client.post(
            "/api/paddle/webhook",
            data=json.dumps(event),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "license_created"
        assert data["plan"] == "pro"
        mock_fb.create_license.assert_called_once()

    def test_webhook_unknown_event(self, client):
        event = {"event_type": "unknown.event", "data": {}}
        resp = client.post(
            "/api/paddle/webhook",
            data=json.dumps(event),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "ignored"


class TestAIEndpoints:
    @patch("server.routes.ai.get_gemini_client")
    def test_suggest_widget(self, mock_get_client, client):
        mock_client = MagicMock()
        mock_client.suggest_widgets.return_value = {"widgets": []}
        mock_get_client.return_value = mock_client
        resp = client.post(
            "/api/ai/suggest-widget",
            data=json.dumps({"developer_task": "fashion app"}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_suggest_widget_no_body(self, client):
        resp = client.post("/api/ai/suggest-widget", content_type="application/json")
        assert resp.status_code == 400

    @patch("server.routes.ai.get_gemini_client")
    def test_generate_content(self, mock_get_client, client):
        mock_client = MagicMock()
        mock_client.generate_widget_content.return_value = {"type": "banner", "params": {"text": "Hello"}}
        mock_get_client.return_value = mock_client
        resp = client.post(
            "/api/ai/generate-content",
            data=json.dumps({"widget_type": "banner", "context": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 200


class TestPlanEnforcement:
    @patch("server.routes.widgets.fb")
    def test_widget_limit_exceeded(self, mock_fb, client):
        mock_fb.get_license.return_value = {"active": True, "plan": "starter", "widget_limit": 3}
        mock_fb.count_widgets_for_license.return_value = 3
        resp = client.post(
            "/api/widgets?api_key=intyx_starter_abc",
            data=json.dumps({"type": "banner", "params": {"text": "test"}, "license_key": "intyx_starter_abc"}),
            content_type="application/json",
        )
        assert resp.status_code == 403
        data = json.loads(resp.data)
        assert "limit" in data["error"].lower()

    @patch("server.routes.widgets.fb")
    def test_widget_within_limit(self, mock_fb, client):
        mock_fb.get_license.return_value = {"active": True, "plan": "pro", "widget_limit": 10}
        mock_fb.count_widgets_for_license.return_value = 2
        mock_fb.create_widget.return_value = "new_id"
        resp = client.post(
            "/api/widgets",
            data=json.dumps({"type": "banner", "params": {"text": "test"}, "license_key": "intyx_pro_abc"}),
            content_type="application/json",
        )
        assert resp.status_code == 201


class TestNotFound:
    def test_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
