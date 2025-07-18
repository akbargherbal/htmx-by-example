# Principal Engineer's Note on Testing Infrastructure:
# This `conftest.py` file is the standard, mandatory setup for our E2E tests.
# Its sole purpose is to provide the `live_server` fixture.
#
# Why this is important:
# - Isolation: The `scope="session"` ensures the server is started only once for the entire
#   test run, which is efficient.
# - Automation: Pytest automatically discovers and uses this fixture in any test function
#   that lists `live_server` as an argument.
# - Reliability: It runs the actual FastAPI application in a background thread, allowing
#   Playwright (our browser testing tool) to interact with it exactly as a real user would.
#
# This file should not be modified. It is a foundational piece of our testing strategy.

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