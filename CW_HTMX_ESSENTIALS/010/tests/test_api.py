# This file contains the API tests for our FastAPI application.
# As a Principal Engineer, I emphasize that tests must be clear, isolated,
# and directly verify the behavior specified in the API contract.
# We use FastAPI's TestClient for synchronous, easy-to-write API tests.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. It automatically runs
# before each test function (`autouse=True`), calling our reset utility.
# This guarantees that every test starts from a known, clean state,
# preventing tests from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it sets up the test application just once for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_get_flights_returns_correct_html_fragment():
    """
    Verifies that GET /api/flights returns a 200 OK and the correct HTML
    table rows fragment, as defined in the API contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/api/flights")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for key data points to ensure the fragment is rendered correctly.
    assert 'data-testid="flight-row-link-FL123-updated"' in response.text
    assert "New York (JFK)" in response.text
    assert "A2 (Gate Change)" in response.text
    assert "Boarding" in response.text
    assert 'data-testid="flight-row-link-BA456-updated"' in response.text
    assert "On Time" in response.text


def test_post_announce_gate_change_returns_hx_trigger_header():
    """
    Verifies that POST /api/announce-gate-change returns a 200 OK with the
    'HX-Trigger' header and an empty body.
    """
    # 1. Arrange & Act
    response = client.post("/api/announce-gate-change")

    # 2. Assert
    assert response.status_code == 200
    # The presence and exact value of this header is the critical part of the contract.
    assert response.headers["hx-trigger"] == "urgentUpdate"
    # The contract specifies no response body.
    assert response.text == ""


def test_post_scan_pass_returns_hx_redirect_header():
    """
    Verifies that POST /api/scan-pass with 'Standard' ticket data returns a
    200 OK with the 'HX-Redirect' header pointing to the correct URL.
    """
    # 1. Arrange & Act: Post form data to the endpoint.
    response = client.post("/api/scan-pass", data={"ticket-type": "Standard"})

    # 2. Assert
    assert response.status_code == 200
    # This header is the key outcome, instructing the client to navigate.
    assert response.headers["hx-redirect"] == "/access-denied"
    # The contract specifies no response body.
    assert response.text == ""


def test_get_flight_details_returns_correct_html_fragment():
    """
    Verifies that GET /flights/{flight_id} returns a 200 OK and the correct
    HTML details fragment for the specified flight.
    """
    # 1. Arrange & Act
    response = client.get("/flights/FL123")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for key data points from the in-memory state.
    assert 'Flight FL123 Details' in response.text
    assert 'Destination:</span> New York (JFK)' in response.text
    assert 'Airline:</span> American Airlines' in response.text
    assert 'Gate:</span> <span class="text-orange-400">A2 (Gate Change)</span>' in response.text


def test_get_access_denied_page_returns_full_html():
    """
    Verifies that GET /access-denied returns a 200 OK and the full,
    correctly formatted HTML page for the access denied screen.
    """
    # 1. Arrange & Act
    response = client.get("/access-denied")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for key content to confirm the correct page was served.
    assert "<title>Access Denied</title>" in response.text
    assert '<h1 class="text-5xl font-extrabold text-red-500">ACCESS DENIED</h1>' in response.text
    assert "Standard tickets do not grant access to this area." in response.text