# Principal Frontend Engineer Notes:
# This file provides the `live_server` fixture required by Playwright tests.
# Its purpose is to run the FastAPI application in a background thread so that
# the browser has a real, running server to connect to during E2E tests.
# This code is standard boilerplate for testing FastAPI with Playwright and
# should not be modified, as per the project's testing guide. It ensures a
# consistent and reliable testing environment for all E2E test suites.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

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

@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """
    This fixture automatically resets the application's in-memory state before each test.
    This is CRITICAL for test isolation. It ensures that actions in one test (like a POST
    request changing data) do not affect the outcome of another test. Each test starts
    from a predictable, clean slate.
    """
    reset_state_for_testing()