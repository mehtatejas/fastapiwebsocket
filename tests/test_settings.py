from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_websocket_settings():
    client = TestClient(app)
    headers = {
        "Authorization": "Bearer dummy-test-token"
    }
    unique_key = f"theme_{uuid.uuid4()}"
    with client.websocket_connect("/ws/settings", headers=headers) as ws:
        # Normal create
        ws.send_json({"action": "create", "payload": {"key": unique_key, "value": "dark"}})
        data = ws.receive_json()
        assert data["action"] == "created"
        assert data["payload"]["key"] == unique_key
        assert data["payload"]["value"] == "dark"
        setting_id = data["payload"]["id"]

        # Read
        ws.send_json({"action": "read"})
        data = ws.receive_json()
        assert data["action"] == "list"
        assert any(item["key"] == unique_key for item in data["payload"])

        # Update
        ws.send_json({"action": "update", "payload": {"id": setting_id, "key": unique_key, "value": "light"}})
        data = ws.receive_json()
        assert data["action"] == "updated"
        assert data["payload"]["value"] == "light"

        # Delete
        ws.send_json({"action": "delete", "payload": {"id": setting_id}})
        data = ws.receive_json()
        assert data["action"] == "deleted"
        assert data["payload"]["id"] == setting_id

        # Invalid payload
        ws.send_json({"action": "create", "payload": {"bad_field": 123}})
        data = ws.receive_json()
        assert data["action"] == "error"

        # Invalid action
        ws.send_json({"action": "notarealaction"})
        data = ws.receive_json()
        assert data["action"] == "error"
