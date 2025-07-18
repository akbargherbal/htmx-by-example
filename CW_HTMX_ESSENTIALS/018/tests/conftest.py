# Principal Engineer's Note:
# This file provides a standard 'live_server' fixture required by pytest-playwright.
# Its purpose is to run the FastAPI application in a background thread, making it
# accessible to the Playwright browser instance at a real network address (e.g., http://127.0.0.1:8000).
# This setup is essential for true end-to-end testing, as it simulates the complete
# client-server interaction. The code is standard and should not be modified.

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