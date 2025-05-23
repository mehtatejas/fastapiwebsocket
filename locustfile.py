
import websocket
import json
from locust import User, task, between, events


class WebSocketClient:
    def __init__(self, host):
        self.host = host
        self.connection = None

    def connect(self, path="/ws/todo"):
        self.connection = websocket.create_connection(
            f"{self.host}{path}",
            header=["Authorization: Bearer dummy-test-token"]
        )

    def send_message(self, message):
        self.connection.send(message)
        return self.connection.recv()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

import time

class WebSocketUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        self.client = WebSocketClient("ws://localhost:8000")

    @task(3)
    def send_create_todo(self):
        """Covers normal create todo path."""
        msg = json.dumps({"action": "create", "payload": {"title": "load test via WS"}})
        self.client.connect()
        start_time = time.time()
        try:
            response = self.client.send_message(msg)
            total_time = int((time.time() - start_time) * 1000)  # ms
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/todo/create",
                response_time=total_time,
                response_length=len(response),
                exception=None,
            )
            print("Response:", response)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/todo/create",
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            print("WebSocket error:", e)
        finally:
            self.client.close()

    @task(1)
    def send_invalid_payload(self):
        """Covers error handling for invalid payload."""
        msg = json.dumps({"action": "create", "payload": {"bad_field": 123}})
        self.client.connect()
        start_time = time.time()
        try:
            response = self.client.send_message(msg)
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/todo/invalid_payload",
                response_time=total_time,
                response_length=len(response),
                exception=None,
            )
            print("Invalid payload response:", response)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/todo/invalid_payload",
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            print("WebSocket error (invalid payload):", e)
        finally:
            self.client.close()

    @task(1)
    def send_to_settings_ws(self):
        """Covers /ws/settings endpoint."""
        msg = json.dumps({"action": "get", "payload": {}})
        self.client.connect(path="/ws/settings")
        start_time = time.time()
        try:
            response = self.client.send_message(msg)
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/settings/get",
                response_time=total_time,
                response_length=len(response),
                exception=None,
            )
            print("Settings response:", response)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/settings/get",
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            print("WebSocket error (settings):", e)
        finally:
            self.client.close()

    @task(1)
    def send_to_teams_ws(self):
        """Covers /ws/teams endpoint."""
        msg = json.dumps({"action": "get", "payload": {}})
        self.client.connect(path="/ws/teams")
        start_time = time.time()
        try:
            response = self.client.send_message(msg)
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/teams/get",
                response_time=total_time,
                response_length=len(response),
                exception=None,
            )
            print("Teams response:", response)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/teams/get",
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            print("WebSocket error (teams):", e)
        finally:
            self.client.close()

    @task(1)
    def connect_failure(self):
        """Covers connection failure path."""
        try:
            # Intentionally use a bad port to force failure
            bad_client = WebSocketClient("ws://localhost:9999")
            bad_client.connect()
        except Exception as e:
            self.environment.events.request.fire(
                request_type="WS",
                name="/ws/connection_failure",
                response_time=0,
                response_length=0,
                exception=e,
            )
            print("Expected connection failure:", e)
