# tests/test_api.py

# This file contains the API-level tests for our FastAPI application.
# The primary goal here is to verify that each endpoint strictly adheres to its
# contract, checking status codes, headers (implicitly), and the exact HTML body.
# We use FastAPI's TestClient, which provides a simple and effective way to
# make requests to the app without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. By using `autouse=True`,
# it automatically runs before every single test function in this file.
# This guarantees that each test starts from a known, clean state,
# preventing tests from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level.
# This is efficient as it sets up the test client a single time for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_get_renovation_item_returns_correct_html():
    """
    Verifies that GET /renovation/item returns a 200 OK and the specific
    HTML fragment for a new glass pane, as per the API contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/renovation/item")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert 'data-testid="new-item-1"' in response.text
    assert "A shiny new glass pane" in response.text
    # A good test is specific. We check for both the test-id and the content.

def test_get_door_assembly_returns_full_component():
    """
    Verifies that GET /hardware-store/door-assembly returns a 200 OK and the
    full HTML component, including the target element for hx-select.
    """
    # 1. Arrange & Act
    response = client.get("/hardware-store/door-assembly")

    # 2. Assert
    assert response.status_code == 200
    # We must verify that the specific element targeted by hx-select is present.
    assert "id='doorknob'" in response.text
    assert "A brass doorknob" in response.text
    # Also check for other parts to ensure the full component was returned.
    assert "A sturdy oak door panel." in response.text

def test_post_custom_cabinet_order_returns_sized_html():
    """
    Verifies that POST /order/custom-cabinet correctly processes form data
    and returns a 200 OK with an HTML fragment reflecting the input width.
    """
    # 1. Arrange: Define the form data to be sent.
    form_data = {"width": "175cm"}

    # 2. Act: Make the POST request with the form data.
    response = client.post("/order/custom-cabinet", data=form_data)

    # 3. Assert
    assert response.status_code == 200
    # The test must confirm that the input data was correctly used in the response.
    assert 'data-testid="custom-cabinet"' in response.text
    assert 'style="width: 175cm; max-width: 100%;"' in response.text
    assert "Custom Cabinet (Width: 175cm)" in response.text