# Principal Frontend Engineer Notes:
# This file provides a standard 'live_server' fixture required by pytest-playwright
# to run the FastAPI application in a background thread. This makes the web server
# available at a local address (e.g., http://127.0.0.1:8000) for the E2E browser
# tests to connect to. This code is standard boilerplate for this type of testing
# and should not be modified unless the application's startup process changes.
# The `scope="session"` argument is an optimization that runs the server only
# once for the entire test session, rather than for each test function, which
# significantly speeds up the test suite.

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