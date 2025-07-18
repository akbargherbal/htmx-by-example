# Principal Engineer Note:
# This file provides the `live_server` fixture, a standard and essential
# component for running end-to-end tests with a real web server.
# It runs the FastAPI application in a background thread, allowing Playwright
# to interact with it as a real user would.
# This code is boilerplate as per the project's testing guide and should not be modified.

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