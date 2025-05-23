from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.db import Base, engine
from app.models import todo, settings, teams
from app.auth import verify_token
from app.websocket.todo import handle_todo_socket
from app.websocket.settings import handle_settings_socket
from app.websocket.teams import handle_teams_socket

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.time() - start)
        return response

app.add_middleware(TimerMiddleware)

@app.websocket("/ws/todo")
async def websocket_todo(websocket: WebSocket):
    await websocket.accept()
    token = websocket.headers.get("authorization", "").replace("Bearer ", "")
    await verify_token(token)
    await handle_todo_socket(websocket)

@app.websocket("/ws/settings")
async def websocket_settings(websocket: WebSocket):
    await websocket.accept()
    token = websocket.headers.get("authorization", "").replace("Bearer ", "")
    await verify_token(token)
    await handle_settings_socket(websocket)

@app.websocket("/ws/teams")
async def websocket_teams(websocket: WebSocket):
    await websocket.accept()
    token = websocket.headers.get("authorization", "").replace("Bearer ", "")
    await verify_token(token)
    await handle_teams_socket(websocket)
