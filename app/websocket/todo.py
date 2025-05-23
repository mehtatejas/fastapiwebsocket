import json, uuid
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.db import SessionLocal

# Add logging to debug potential issues causing test_todo to hang
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("todo_websocket")

async def handle_todo_socket(websocket: WebSocket):
    db: Session = SessionLocal()
    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received data: {data}")
            except Exception as e:
                logger.error(f"[WebSocket] receive_text error: {e}")
                break
            msg = json.loads(data)
            action = msg.get("action")
            payload = msg.get("payload", {})
            response = {}

            try:
                if action == "create":
                    todo = Todo(id=str(uuid.uuid4()), title=payload.get("title"), completed=False)
                    db.add(todo)
                    db.commit()
                    db.refresh(todo)
                    response = {"action": "created", "payload": {"id": todo.id, "title": todo.title, "completed": todo.completed}}

                elif action == "read":
                    try:
                        todos = db.query(Todo).all()
                        response = {
                            "action": "list",
                            "payload": [
                                {"id": t.id, "title": t.title, "completed": t.completed} for t in todos
                            ]
                        }
                        logger.debug(f"Read action successful: {response}")
                    except Exception as e:
                        logger.error(f"Error during read action: {e}")
                        response = {"action": "error", "payload": str(e)}

                elif action == "update":
                    todo = db.get(Todo, payload.get("id"))
                    if todo:
                        todo.title = payload.get("title", todo.title)
                        todo.completed = payload.get("completed", todo.completed)
                        db.commit()
                        response = {"action": "updated", "payload": {"id": todo.id, "title": todo.title, "completed": todo.completed}}

                elif action == "delete":
                    todo = db.get(Todo, payload.get("id"))
                    if todo:
                        db.delete(todo)
                        db.commit()
                        response = {"action": "deleted", "payload": {"id": todo.id}}

                else:
                    response = {"action": "error", "payload": "Invalid action"}

                logger.debug(f"Action: {action}, Response: {response}")
            except Exception as e:
                logger.error(f"[WebSocket] handler error: {e}")
                response = {"action": "error", "payload": str(e)}

            await websocket.send_text(json.dumps(response))
    except Exception as e:
        logger.error(f"[WebSocket] outer error: {e}")
    finally:
        db.close()
        logger.debug("Database connection closed.")
