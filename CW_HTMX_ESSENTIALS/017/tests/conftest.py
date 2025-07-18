# This comment explains the purpose of the conftest.py file.
# It provides a standard 'live_server' fixture to run the FastAPI app
# in the background, making it available for E2E browser tests.
# This code is standard across projects and ensures a consistent testing environment.
import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread for the entire test session."""
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    yield server
    server.should_exit = True
    thread.join()

@pytest.fixture(autouse=True)
def reset_state_before_each_e2e_test():
    """
    This fixture automatically runs before each E2E test function.
    It calls the state reset function from the main application. This is a critical
    best practice for E2E testing against a stateful in-memory backend. It ensures
    that every test starts from a clean, predictable state, preventing tests from
    interfering with each other and leading to flaky results.
    """
    reset_state_for_testing()