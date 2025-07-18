# This file contains the API-level tests for our FastAPI application.
# The goal is to verify that each endpoint behaves exactly as defined in the
# API Contract, checking status codes, headers, and response bodies.
# We use FastAPI's TestClient, which provides a simple and efficient way
# to make requests to the app without running a live server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing # Import the app and reset utility

# This fixture is a cornerstone of reliable testing. By using `autouse=True`,
# it automatically runs before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state,
# ensuring test isolation and preventing cascading failures.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it sets up the client a single time for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_process_address_change_success():
    """
    Verifies the happy-path scenario for the address change endpoint.
    It sends valid form data and asserts that the response is a 200 OK
    and contains the correctly formatted success message.
    """
    # 1. Arrange: Define the form data to be sent in the POST request.
    # This mimics a user filling out and submitting the form.
    form_data = {
        "street": "123 Main St",
        "zip_code": "90210",
        "customer-id": "CUST-999",
        "service_type": "Priority"
    }

    # 2. Act: Make the POST request to the endpoint with the form data.
    response = client.post("/process-address-change", data=form_data)

    # 3. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Success!" in response.text
    assert "CUST-999" in response.text
    assert "Priority" in response.text
    assert "123 Main St" in response.text
    assert "90210" in response.text

def test_process_invalid_zip_returns_404_error():
    """
    Verifies that the invalid zip endpoint correctly returns a 404 Not Found status.
    This test ensures our application properly handles this specific error case
    as defined in the contract.
    """
    # 1. Act: Make a POST request to the endpoint that simulates the error.
    response = client.post("/process-invalid-zip")

    # 2. Assert: Check for the 404 status code and the specific error message.
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Error: Not Found (404)" in response.text
    assert "zip code could not be found" in response.text

def test_simulate_server_failure_returns_500_error():
    """
    Verifies that the server failure simulation endpoint returns a 500 Internal Server Error.
    This confirms the application can generate the specified server-side error response.
    """
    # 1. Act: Make a POST request to the endpoint that simulates the failure.
    response = client.post("/simulate-server-failure")

    # 2. Assert: Check for the 500 status code and the corresponding error message.
    assert response.status_code == 500
    assert "text/html" in response.headers["content-type"]
    assert "Error: Internal Server Error (500)" in response.text
    assert "mail sorting machine is offline" in response.text