# This file contains shared pytest fixtures.
# As per the project's testing guide, this provides a standard `live_server`
# fixture to run the FastAPI application in a background thread. This makes the
# application accessible over HTTP for our Playwright end-to-end tests,
# simulating a real user environment. This code is standardized for the course.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread."""
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
    This is a critical fixture for ensuring test isolation.
    By marking it with `autouse=True`, pytest will run this fixture before every
    single test function. It calls our `reset_state_for_testing` function from
    the main app, which clears the in-memory `EXHIBITS` dictionary. This guarantees
    that each test starts with a clean, predictable application state, preventing
    side effects from one test from influencing another.
    """
    reset_state_for_testing()