# Principal Frontend Engineer Notes:
# This file provides the necessary setup for our end-to-end (E2E) tests.
# The `live_server` fixture is a standard pattern for testing web applications with pytest.
# It starts the FastAPI application in a separate, background thread before the tests run,
# and shuts it down after they complete. This allows Playwright to access a real,
# running instance of our application at a known address (http://127.0.0.1:8000).
# This code is standardized and should not be modified, as per the testing guide.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing  # Import the FastAPI app and state reset function

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread for the entire test session."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
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
    This is CRITICAL for test isolation. Without it, an order placed in one test would
    still exist in the `app_state` for the next test, leading to unpredictable and
    unreliable test results. `autouse=True` ensures it runs for every single test function.
    """
    reset_state_for_testing()