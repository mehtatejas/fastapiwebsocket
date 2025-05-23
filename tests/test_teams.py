from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_websocket_teams():
    client = TestClient(app)
    headers = {
        "Authorization": "Bearer dummy-test-token"
    }
    unique_name = f"dev_team_{uuid.uuid4()}"
    with client.websocket_connect("/ws/teams", headers=headers) as ws:
        # Normal create
        ws.send_json({"action": "create", "payload": {"name": unique_name, "description": "backend developers"}})
        data = ws.receive_json()
        assert data["action"] == "created"
        assert data["payload"]["name"] == unique_name
        assert data["payload"]["description"] == "backend developers"
        team_id = data["payload"]["id"]

        # Read
        ws.send_json({"action": "read"})
        data = ws.receive_json()
        assert data["action"] == "list"
        assert any(item["name"] == unique_name for item in data["payload"])

        # Update
        ws.send_json({"action": "update", "payload": {"id": team_id, "name": unique_name, "description": "frontend developers"}})
        data = ws.receive_json()
        assert data["action"] == "updated"
        assert data["payload"]["description"] == "frontend developers"

        # Delete
        ws.send_json({"action": "delete", "payload": {"id": team_id}})
        data = ws.receive_json()
        assert data["action"] == "deleted"
        assert data["payload"]["id"] == team_id

        # Invalid payload
        ws.send_json({"action": "create", "payload": {"bad_field": 123}})
        data = ws.receive_json()
        assert data["action"] == "error"

        # Invalid action
        ws.send_json({"action": "notarealaction"})
        data = ws.receive_json()
        assert data["action"] == "error"
