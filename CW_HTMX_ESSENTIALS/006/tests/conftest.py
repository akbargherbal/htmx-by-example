# Principal Frontend Engineer Notes:
# This file provides a standard 'live_server' fixture required by pytest-playwright
# to run end-to-end tests.
# - Purpose: It starts the FastAPI application in a background thread before the tests run.
# - Scope: `scope="session"` is a crucial optimization. It ensures the server is started
#   only once for the entire test session, not for each individual test function,
#   which significantly speeds up the test suite execution.
# - Teardown: The `yield` statement passes control to the tests. After all tests
#   in the session are complete, the code after `yield` executes, gracefully
#   shutting down the server. This is essential for clean test runs.

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