# Principal Frontend Engineer's Notes:
# This file provides a standard 'live_server' fixture required by pytest-playwright
# to conduct end-to-end tests. Its purpose is to run our FastAPI application
# in a background thread, making it accessible to the Playwright browser instance.
#
# This code is boilerplate as defined by the project's testing guide. It is
# designed to be robust and reusable across different lessons. There is no need
# to modify this file.
#
# Key components:
# - `pytest.fixture(scope="session")`: This decorator registers `live_server` as a
#   pytest fixture. The `scope="session"` means the server is started only once
#   for the entire test session, which is highly efficient.
# - `uvicorn.Server`: We use uvicorn programmatically to run the FastAPI `app`.
# - `threading.Thread`: The server runs in a separate thread so it doesn't block
#   the main pytest process. `daemon=True` ensures the thread exits when the
#   main process does.
# - `yield server`: This is the magic of pytest fixtures. The code before the `yield`
#   is the setup (start the server). The test functions run at this point. The code
#   after the `yield` is the teardown (stop the server).

import pytest
import uvicorn
import threading
from app.main import app  # Import the FastAPI app object from our application code

@pytest.fixture(scope="session")
def live_server():
    """Pytest fixture to run the FastAPI app in a background thread."""
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    yield server
    # Teardown: Gracefully stop the server after the test session is complete.
    server.should_exit = True
    thread.join()