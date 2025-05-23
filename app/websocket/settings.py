import json, uuid
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.models.settings import Setting
from app.db import SessionLocal

async def handle_settings_socket(websocket: WebSocket):
    db: Session = SessionLocal()
    try:
        while True:
            try:
                data = await websocket.receive_text()
            except Exception as e:
                print(f"[WebSocket] receive_text error: {e}")
                break
            msg = json.loads(data)
            action = msg.get("action")
            payload = msg.get("payload", {})
            response = {}

            try:
                if action == "create":
                    setting = Setting(id=str(uuid.uuid4()), key=payload.get("key"), value=payload.get("value"))
                    db.add(setting)
                    db.commit()
                    db.refresh(setting)
                    response = {"action": "created", "payload": {"id": setting.id, "key": setting.key, "value": setting.value}}

                elif action == "read":
                    settings = db.query(Setting).all()
                    response = {
                        "action": "list",
                        "payload": [
                            {"id": s.id, "key": s.key, "value": s.value} for s in settings
                        ]
                    }

                elif action == "update":
                    setting = db.get(Setting, payload.get("id"))
                    if setting:
                        setting.key = payload.get("key", setting.key)
                        setting.value = payload.get("value", setting.value)
                        db.commit()
                        response = {"action": "updated", "payload": {"id": setting.id, "key": setting.key, "value": setting.value}}

                elif action == "delete":
                    setting = db.get(Setting, payload.get("id"))
                    if setting:
                        db.delete(setting)
                        db.commit()
                        response = {"action": "deleted", "payload": {"id": setting.id}}

                else:
                    response = {"action": "error", "payload": "Invalid action"}
            except Exception as e:
                print(f"[WebSocket] handler error: {e}")
                response = {"action": "error", "payload": str(e)}

            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print(f"[WebSocket] outer error: {e}")
    finally:
        db.close()
