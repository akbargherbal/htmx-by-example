# Principal Frontend Engineer Notes:
# This file provides a standard 'live_server' fixture required by pytest-playwright
# to run the FastAPI application in a background thread.
# This makes the web server available at a real address (e.g., http://127.0.0.1:8000)
# for the Playwright browser instance to connect to.
# This code is standard boilerplate for testing FastAPI with Playwright and should not be modified.
# The `scope="session"` means the server is started once per test session, which is efficient.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread."""
    # We run the server on a specific host and port for predictable test URLs.
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    # The `yield` passes control to the test function.
    yield server
    # After the tests are done, we gracefully shut down the server.
    server.should_exit = True
    thread.join()

@pytest.fixture(autouse=True)
def reset_state_before_each_test(live_server):
    """
    This is a critical fixture for ensuring test isolation.
    By using `autouse=True`, it automatically runs before every single test function.
    It calls the `reset_state_for_testing` function from our application, which clears
    the in-memory credit and item stock. This prevents one test from impacting the results of another.
    """
    reset_state_for_testing()