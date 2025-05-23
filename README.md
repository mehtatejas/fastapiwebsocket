# fastapiwebsocket

## Running the FastAPI WebSocket Server

1. **Install dependencies** (if not already installed):
   ```zsh
   uv pip install -r requirements.txt  # or use 'uv pip install .' if using pyproject.toml
   ```

2. **Start the server**:
   ```zsh
   uv run uvicorn app.main:app --reload
   ```
   The server will be available at http://localhost:8000

## Running Tests

To run all tests using pytest:
```zsh
uv run pytest --capture=tee-sys --cov=app --cov=tests --cov-report=term-missing
```

## Load Testing (optional)

To run load tests with Locust (WebSocket):

1. **Install the required package** (if not already installed):
   ```zsh
   uv pip install websocket-client
   ```

2. **Start the FastAPI server** in a separate terminal:
   ```zsh
   uv run uvicorn app.main:app --reload
   ```

3. **Run Locust load test**:
   ```zsh
   uv run locust -f locustfile.py --headless -u 10 -r 2 --run-time 30s --host http://localhost:8000
   ```

**Parameter explanations:**
- `-u` or `--users`: Number of simulated users (WebSocket clients).
- `-r` or `--spawn-rate`: How many users to start per second.
- `--run-time`: How long the test should run (e.g., `30s`, `1m`, `5m`).
- `--host`: The base URL of your FastAPI server.
- `--headless`: Runs Locust without the web UI, outputs results to the terminal.

After the test completes, Locust will print a summary of results (requests, failures, and statistics) in your terminal. Since the script uses a custom WebSocket client, detailed request stats may not appear unless custom event logging is added.

The Locust script uses a synchronous WebSocket client for compatibility with Locust's threading model.