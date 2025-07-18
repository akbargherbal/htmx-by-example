# Principal Frontend Engineer Notes:
# This file provides the standard `live_server` fixture required by the E2E testing guide.
# Its purpose is to run the FastAPI application in a background thread so that Playwright
# can access it via a real HTTP server (e.g., http://127.0.0.1:8000).
# This setup is crucial for true end-to-end tests, as it exercises the full application stack,
# from the browser's HTTP request to the server's response.
# The `scope="session"` ensures the server is started only once for the entire test run,
# which is efficient. The code is standard and should not be modified.

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