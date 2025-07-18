# Principal Engineer's Note:
# This file provides the standard `live_server` fixture required by Playwright
# to run end-to-end tests against a real, running instance of our application.
#
# The `scope="session"` argument is a crucial optimization. It ensures that the
# FastAPI server is started only once for the entire test session, rather than
# being torn down and set up for each individual test function. This significantly
# speeds up the execution of the test suite.
#
# This code is standardized as per the project's testing guide and should not
# be modified.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

@pytest.fixture(autouse=True)
def reset_state_before_each_e2e_test():
    """
    This fixture automatically resets the application's in-memory state before
    every single E2E test. This is critical for test isolation, ensuring that
    actions in one test (like adding a song to the queue) do not affect the
    outcome of another test.
    """
    reset_state_for_testing()

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