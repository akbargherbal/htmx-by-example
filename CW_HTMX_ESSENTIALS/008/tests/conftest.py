# Principal Frontend Engineer Notes:
# This file provides the `live_server` fixture, a non-negotiable component for reliable E2E testing.
#
# Purpose:
# The `live_server` fixture starts the FastAPI application in a background thread before the test session begins
# and shuts it down after the session ends. This ensures that our Playwright tests have a real, running
# server to interact with, allowing us to test the complete request-response cycle from the browser's perspective.
#
# Implementation Details:
# - `scope="session"`: This is a crucial optimization. The server is started only once per test session,
#   not for every single test function, which significantly speeds up the test suite.
# - `threading`: We use a separate thread for the Uvicorn server so that it doesn't block the main pytest thread,
#   allowing the tests to execute.
# - `yield`: The `yield` keyword passes control to the test session while the server is running. Code after the
#   `yield` is the teardown logic, which ensures the server is cleanly shut down.
#
# This code is standardized as per our project's testing guide and should not be modified.

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