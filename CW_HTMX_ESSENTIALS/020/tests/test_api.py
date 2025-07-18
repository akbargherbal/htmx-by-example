# This file contains the API-level tests for our FastAPI application.
# The goal is to verify that each endpoint strictly conforms to the API contract
# regarding status codes, headers, and response bodies. We use FastAPI's TestClient
# for this purpose, as it provides a direct and efficient way to test the app
# without a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This pytest fixture is decorated with `autouse=True`, which means it will
# automatically run before every single test function in this file.
# This is the cornerstone of test isolation, ensuring no state leaks between tests.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it sets up the application wrapper only once for all tests in this file.
client = TestClient(app)


# --- Test Cases ---

def test_mix_chemicals_standard_success():
    """
    Verifies the standard success case for POST /mix.
    It checks for a 200 OK status, the correct success message in the HTML
    response, and ensures the special HX-Trigger header is NOT present.
    """
    # 1. Arrange: Define the form data for the request.
    payload = {"chemical_a": "Water", "chemical_b": "Salt"}

    # 2. Act: Make the POST request to the endpoint.
    response = client.post("/mix", data=payload)

    # 3. Assert: Verify all parts of the API contract.
    assert response.status_code == 200
    assert "HX-Trigger" not in response.headers
    assert "Mix complete: Water + Salt formed." in response.text
    assert 'class="text-green-400"' in response.text


def test_mix_chemicals_triggers_alert_on_specific_combo():
    """
    Verifies the conditional logic for POST /mix.
    It confirms that when the specific "risky" chemicals are mixed, the
    response includes the `HX-Trigger: VENT_NOW` header as per the contract.
    """
    # 1. Arrange: Define the special form data that triggers the alert.
    payload = {"chemical_a": "Acidic Reagent", "chemical_b": "Volatile Catalyst"}

    # 2. Act: Make the POST request.
    response = client.post("/mix", data=payload)

    # 3. Assert: Verify status, header, and body.
    assert response.status_code == 200
    assert "HX-Trigger" in response.headers
    assert response.headers["HX-Trigger"] == "VENT_NOW"
    assert "Mix complete: Acidic Reagent + Volatile Catalyst formed." in response.text


def test_risky_mix_fails_with_422_status():
    """
    Verifies that the POST /risky-mix endpoint correctly returns a 422
    Unprocessable Entity status code and the specified error message. This
    confirms the failure path of the API contract.
    """
    # 1. Arrange & 2. Act: Make the POST request. No payload is needed.
    response = client.post("/risky-mix")

    # 3. Assert: Check for the specific error status and message.
    assert response.status_code == 422
    assert "Useless brown sludge formed" in response.text
    assert 'class="text-red-400"' in response.text


def test_get_temperature_returns_initial_state():
    """
    Verifies that the GET /temperature endpoint returns the initial temperature
    from the application's state. This is crucial for testing polling endpoints.
    """
    # 1. Arrange & 2. Act: Make a simple GET request.
    response = client.get("/temperature")

    # 3. Assert: Check the status and that the body contains the initial value.
    # The initial temperature is 22, as defined in the reset_state_for_testing function.
    assert response.status_code == 200
    assert response.text == "22°C"