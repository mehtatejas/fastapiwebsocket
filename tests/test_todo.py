from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_websocket_todo():
    client = TestClient(app)
    headers = {
        "Authorization": "Bearer dummy-test-token"
    }
    unique_title = f"test_task_{uuid.uuid4()}"
    with client.websocket_connect("/ws/todo", headers=headers) as ws:
        # Normal create
        print("SEND: create")
        ws.send_json({"action": "create", "payload": {"title": unique_title}})
        data = ws.receive_json()
        print("RECV:", data)
        assert data["action"] == "created"
        assert data["payload"]["title"] == unique_title
        todo_id = data["payload"]["id"]

        # Read
        print("SEND: read")
        ws.send_json({"action": "read"})
        data = ws.receive_json()
        print("RECV:", data)
        assert data["action"] == "list"
        assert any(item["title"] == unique_title for item in data["payload"])

        # Update
        print("SEND: update")
        ws.send_json({"action": "update", "payload": {"id": todo_id, "title": unique_title + "_upd", "completed": True}})
        data = ws.receive_json()
        print("RECV:", data)
        assert data["action"] == "updated"
        assert data["payload"]["title"] == unique_title + "_upd"
        assert data["payload"]["completed"] is True

        # Delete
        print("SEND: delete")
        ws.send_json({"action": "delete", "payload": {"id": todo_id}})
        data = ws.receive_json()
        print("RECV:", data)
        assert data["action"] == "deleted"
        assert data["payload"]["id"] == todo_id

        # Invalid payload
        print("SEND: invalid payload")
        try:
            ws.send_json({"action": "create", "payload": {"bad_field": 123}})
            data = ws.receive_json()
            print("RECV:", data)
            assert data["action"] == "error"
        except WebSocketDisconnect as e:
            print(f"WebSocketDisconnect after invalid payload: {e}")

        # Invalid action
        print("SEND: invalid action")
        try:
            ws.send_json({"action": "notarealaction"})
            data = ws.receive_json()
            print("RECV:", data)
            assert data["action"] == "error"
        except WebSocketDisconnect as e:
            print(f"WebSocketDisconnect after invalid action: {e}")