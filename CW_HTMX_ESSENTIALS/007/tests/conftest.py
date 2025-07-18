# Principal Frontend Engineer Notes:
# This file provides the `live_server` fixture, a standard and essential
# component for running end-to-end tests with a real web server.
# It runs the FastAPI application in a background thread, allowing Playwright
# to interact with it as a real user would.
# This code is standardized as per the project's testing guide and should not be modified.
# The `scope="session"` is a performance optimization: the server is started
# once per test session, not for every single test function.

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
def reset_state_before_each_e2e_test(live_server):
    """
    This is a critical fixture for ensuring E2E test isolation.
    Even though we have a live server, we can still call our state reset
    function directly before each test runs. This prevents state from one test
    (e.g., an item added to the order) from leaking into and corrupting the next test.
    The `live_server` dependency ensures the server is running before we try to reset state.
    """
    reset_state_for_testing()