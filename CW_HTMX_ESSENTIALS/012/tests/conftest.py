# Principal Frontend Engineer Notes:
#
# This `conftest.py` file provides a standard `live_server` fixture.
# This is a non-negotiable component for reliable E2E testing, as it ensures
# our FastAPI application is running in a background thread before any
# Playwright tests attempt to access it.
#
# The `scope="session"` argument is a critical optimization. It means the server
# is started only once for the entire test session, rather than being torn down
# and set up for each individual test function. This dramatically speeds up
# the execution of the test suite.
#
# This code is standardized as per the project's testing guide and should not
# be modified.
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