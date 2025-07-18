# Principal Frontend Engineer Notes:
#
# This `conftest.py` file provides a standard `live_server` fixture required by
# pytest-playwright for end-to-end testing.
#
# Purpose:
# - It runs the FastAPI application in a background thread.
# - This makes the application accessible over HTTP (at http://127.0.0.1:8000)
#   for the Playwright browser instance to interact with, just like a real user.
#
# Implementation Details:
# - `scope="session"`: This is a critical optimization. The server is started
#   only once for the entire test session, rather than for each test function.
#   This significantly speeds up the E2E test suite.
# - `threading`: Using a separate thread ensures the test runner is not blocked
#   by the running Uvicorn server.
# - `yield`: The `yield` keyword passes control to the test functions while the
#   server is running. After all tests in the session are complete, the code
#   after `yield` executes to gracefully shut down the server.
#
# This file is standard boilerplate for this project and should not be modified.
import pytest
import uvicorn
import threading
from app.main import app  # Import the FastAPI app object

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread."""
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    yield server
    server.should_exit = True
    thread.join()