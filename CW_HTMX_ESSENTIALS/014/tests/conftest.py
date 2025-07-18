# Principal Frontend Engineer Notes:
# This file provides the standard `live_server` fixture required by the testing guide.
# Its purpose is to run the FastAPI application in a background thread, making it
# accessible to the Playwright browser instance during E2E tests.
# This code is boilerplate for our project and should not be modified unless the
# core application startup logic changes. It ensures a consistent testing
# environment for all E2E test suites.
# The `scope="session"` argument is a critical optimization: it starts the server
# once per test session, rather than for every single test function, which
# significantly speeds up the test suite execution.

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