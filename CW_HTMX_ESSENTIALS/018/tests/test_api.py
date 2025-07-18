# This file contains the automated API tests for our FastAPI application.
# The purpose of these tests is to verify that each endpoint behaves exactly
# as specified in the API Contract, ensuring reliability and correctness.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a core principle of our testing strategy.
# The `autouse=True` argument tells pytest to run this fixture automatically
# before every single test function in this file. This guarantees that the
# application's in-memory state is reset, ensuring each test runs in isolation.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the `TestClient` once at the module level.
# This client allows us to make simulated HTTP requests to our FastAPI app
# without needing to run a live server. It's fast, efficient, and reliable.
client = TestClient(app)


# --- Test Cases ---

def test_request_missing_file_returns_404_and_error_html():
    """
    Verifies that the `/request-file/missing` endpoint correctly returns a
    404 Not Found status and the specific HTML error message, as per the contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/request-file/missing")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 404
    assert 'data-testid="inbox-404-state"' in response.text
    assert "File Not Found" in response.text


def test_request_crashed_server_returns_500_and_error_html():
    """
    Verifies that the `/request/crashed-server` endpoint correctly returns a
    500 Internal Server Error status and the corresponding HTML fragment.
    """
    # 1. Arrange & Act
    response = client.get("/request/crashed-server")

    # 2. Assert
    assert response.status_code == 500
    assert "Server Error" in response.text
    assert "Records Department is currently offline" in response.text


def test_request_old_department_triggers_hx_redirect_header():
    """
    Verifies that a GET request to `/mail/old-department` returns a 200 OK status
    but includes the critical `HX-Redirect` header pointing to the new location.
    It also confirms the response body is empty, as specified.
    """
    # 1. Arrange & Act
    response = client.get("/mail/old-department")

    # 2. Assert
    assert response.status_code == 200
    # The most important assertion: check for the presence and correctness of the header.
    assert "HX-Redirect" in response.headers
    assert response.headers["HX-Redirect"] == "/mail/new-department"
    # Per the contract, the body for a redirect response is empty.
    assert not response.text


def test_get_new_department_returns_success_html():
    """
    Verifies that the redirect target, `/mail/new-department`, can be accessed
    directly and returns a 200 OK status with the expected success message HTML.
    """
    # 1. Arrange & Act
    response = client.get("/mail/new-department")

    # 2. Assert
    assert response.status_code == 200
    assert 'data-testid="inbox-redirect-state"' in response.text
    assert "Your request was rerouted" in response.text