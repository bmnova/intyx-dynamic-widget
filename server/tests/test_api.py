"""Tests for Flask API endpoints."""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock external dependencies that may not be installed in test env
for mod in [
    "firebase_admin", "firebase_admin.credentials", "firebase_admin.firestore",
    "google.generativeai", "mcp", "mcp.server", "mcp.server.stdio", "mcp.types",
]:
    sys.modules.setdefault(mod, MagicMock())

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


class TestNotFound:
    def test_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
