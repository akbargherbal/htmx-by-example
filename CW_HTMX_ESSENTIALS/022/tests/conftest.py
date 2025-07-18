# Principal Frontend Engineer's Notes:
# This `conftest.py` file is standard boilerplate for running E2E tests with
# pytest and a web server framework like FastAPI.
#
# The `live_server` fixture is the key component. It performs the following steps:
# 1. It's scoped to the "session", meaning it starts the server *once* before
#    any tests run and shuts it down *once* after all tests have finished. This is
#    highly efficient.
# 2. It runs the Uvicorn server in a separate background thread (`threading.Thread`).
#    This is crucial because it prevents the server from blocking the main thread
#    where pytest is running the tests.
# 3. The `yield` statement passes control to the test functions. The tests run
#    while the server is live in the background.
# 4. After all tests are complete, the code after `yield` executes, gracefully
#    shutting down the server.
#
# This setup is non-negotiable for reliable E2E testing as it ensures the
# browser has a real, running application to interact with.

import pytest
import uvicorn
import threading
from app.main import app, reset_state_for_testing

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

@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """
    This fixture automatically resets the application's in-memory state
    before each test function runs. This is a critical pattern for ensuring
    test isolation. Each test starts with a clean slate (1 Tomato, 1 Weed),
    preventing the outcome of one test from affecting another.
    """
    reset_state_for_testing()