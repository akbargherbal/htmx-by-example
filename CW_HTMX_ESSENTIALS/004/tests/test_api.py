# This file contains the API tests for our FastAPI application.
# The primary goal is to verify that each endpoint strictly adheres to the defined API contract.
# We use FastAPI's TestClient, which provides a simple and effective way to make requests
# to the application without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. By marking it with `autouse=True`,
# pytest will automatically run this function before every single test function in this file.
# This guarantees that each test starts from a known, clean state, preventing side effects
# and ensuring test independence.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# The TestClient is instantiated once at the module level. This is efficient as it
# sets up the testing infrastructure once, and all subsequent tests can use this
# single client instance to make requests.
client = TestClient(app)


# --- Test Functions (Verifying the API Contract) ---

def test_get_fuel_level_returns_correct_html_and_status():
    """
    Verifies that GET /api/fuel-level returns a 200 OK and the expected HTML fragment.
    This test confirms the happy path for the fuel gauge endpoint.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/api/fuel-level")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert 'Fuel: 98%' in response.text

def test_post_calculate_route_without_tolls_returns_correct_message():
    """
    Verifies that POST /api/calculate-route (without avoiding tolls) returns a 200 OK
    and the correct confirmation message.
    """
    # 1. Arrange & Act: Post form data to the endpoint.
    response = client.post("/api/calculate-route", data={"destination": "City Hall"})

    # 2. Assert: Check status and the specific text for this scenario.
    assert response.status_code == 200
    assert "Route to 'City Hall' via the fastest route" in response.text

def test_post_calculate_route_with_tolls_returns_correct_message():
    """
    Verifies that POST /api/calculate-route (with 'avoid_tolls' checked) returns a 200 OK
    and the corresponding confirmation message.
    """
    # 1. Arrange & Act: Post form data including the 'avoid_tolls' checkbox value.
    response = client.post(
        "/api/calculate-route",
        data={"destination": "The Airport", "avoid_tolls": "on"}
    )

    # 2. Assert: Check status and the specific text for the "avoiding tolls" scenario.
    assert response.status_code == 200
    assert "Route to 'The Airport' avoiding tolls" in response.text

def test_get_tune_invalid_station_returns_404_not_found():
    """
    Verifies that GET /api/tune-invalid-station correctly returns a 404 status code,
    as specified in the contract for a client-side error.
    """
    # 1. Arrange & Act
    response = client.get("/api/tune-invalid-station")

    # 2. Assert: The only thing that matters for this contract item is the status code.
    assert response.status_code == 404

def test_get_check_broken_sensor_returns_500_server_error():
    """
    Verifies that GET /api/check-gps-sensor correctly returns a 500 status code,
    simulating a server-side failure as per the contract.
    """
    # 1. Arrange & Act
    response = client.get("/api/check-gps-sensor")

    # 2. Assert: Verify the 500 status code.
    assert response.status_code == 500

def test_get_race_mode_returns_hx_redirect_header():
    """
    Verifies that GET /page/settings/race-mode returns a 200 OK status but includes
    the critical 'HX-Redirect' header for client-side redirection.
    """
    # 1. Arrange & Act
    response = client.get("/page/settings/race-mode")

    # 2. Assert: Check for both the successful status code and the presence and
    # correctness of the HX-Redirect header.
    assert response.status_code == 200
    assert "HX-Redirect" in response.headers
    assert response.headers["HX-Redirect"] == "/page/driving-mode-selection"

def test_get_driving_mode_selection_page_returns_full_html():
    """
    Verifies that the redirect target, GET /page/driving-mode-selection, serves the
    full, correct HTML page as defined in the contract.
    """
    # 1. Arrange & Act
    response = client.get("/page/driving-mode-selection")

    # 2. Assert: Check for a 200 OK and key elements of the full HTML document.
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "<title>Mode Selection</title>" in response.text
    assert "Driving Mode Selection</h1>" in response.text