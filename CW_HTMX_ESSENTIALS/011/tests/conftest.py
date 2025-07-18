# Principal Engineer's Note:
# This conftest.py file is standard boilerplate for testing a live FastAPI application with Playwright.
# It defines a 'live_server' fixture with 'session' scope, meaning the web server
# is started only once for the entire test session, which is highly efficient.
# The server runs in a background thread, allowing the main thread to execute tests.
# This setup is crucial for reliable E2E tests as it provides a real, running
# application for the browser to interact with.
# This code MUST NOT be modified, as per the testing guide.

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
    Principal Engineer's Note:
    This is a critical fixture for ensuring test isolation. By using `autouse=True`,
    it automatically runs before every single test function. It calls the `reset_state_for_testing`
    function from our application logic, which resets the in-memory database.
    This guarantees that each test starts from a known, clean slate, preventing
    the outcome of one test from affecting another.
    """
    reset_state_for_testing()