import json, uuid
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.models.teams import Team
from app.db import SessionLocal

async def handle_teams_socket(websocket: WebSocket):
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
                    team = Team(id=str(uuid.uuid4()), name=payload.get("name"), description=payload.get("description", ""))
                    db.add(team)
                    db.commit()
                    db.refresh(team)
                    response = {"action": "created", "payload": {"id": team.id, "name": team.name, "description": team.description}}

                elif action == "read":
                    teams = db.query(Team).all()
                    response = {
                        "action": "list",
                        "payload": [
                            {"id": t.id, "name": t.name, "description": t.description} for t in teams
                        ]
                    }

                elif action == "update":
                    team = db.query(Team).get(payload.get("id"))
                    if team:
                        team.name = payload.get("name", team.name)
                        team.description = payload.get("description", team.description)
                        db.commit()
                        response = {"action": "updated", "payload": {"id": team.id, "name": team.name, "description": team.description}}

                elif action == "delete":
                    team = db.query(Team).get(payload.get("id"))
                    if team:
                        db.delete(team)
                        db.commit()
                        response = {"action": "deleted", "payload": {"id": team.id}}

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
