# Principal Frontend Engineer Notes:
# This file provides the standard `live_server` fixture required by Playwright tests.
# Its purpose is to run the FastAPI application in a background thread, making it
# accessible to the Playwright browser instance at a real URL (e.g., http://127.0.0.1:8000).
# This setup is non-negotiable for true end-to-end testing, as it exercises the
# entire stack from the browser to the server.
# The code is standard boilerplate for this type of testing and should not be modified.

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