# This file contains the automated API tests for our FastAPI application.
# It uses FastAPI's TestClient to make requests to the endpoints and verify
# that they behave exactly as specified in the API Contract.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing # Import the app and reset utility

# This fixture is a powerful pytest feature. By setting `autouse=True`, it will
# automatically run before every single test function in this file. This
# guarantees that our application state is reset, ensuring test isolation.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is more efficient
# than creating a new client for every test. The client simulates making
# HTTP requests to our running application.
client = TestClient(app)


# --- Test Functions ---

def test_get_backdrop_painting_returns_correct_html():
    """
    Verifies that GET /set/backdrop-painting returns a 200 OK and the
    correct image HTML fragment as per the API contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/set/backdrop-painting")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert 'src="https://placehold.co/200x150/333333/FFF?text=Stormy+Sea"' in response.text
    assert 'alt="A stormy sea painting"' in response.text

def test_get_fireplace_prop_returns_correct_html():
    """
    Verifies that GET /set/fireplace-prop returns a 200 OK and the
    correct 'Modern Hearth' HTML fragment.
    """
    response = client.get("/set/fireplace-prop")
    assert response.status_code == 200
    assert 'data-testid="fireplace-after"' in response.text
    assert "Modern Hearth" in response.text
    assert "💎" in response.text

def test_get_add_chair_returns_correct_html():
    """
    Verifies that GET /set/add-chair returns a 200 OK and the
    correct 'New Chair' HTML fragment.
    """
    response = client.get("/set/add-chair")
    assert response.status_code == 200
    assert 'data-testid="chair-prop"' in response.text
    assert "New Chair" in response.text
    assert "🪑" in response.text

def test_get_add_coat_rack_returns_correct_html():
    """
    Verifies that GET /set/add-coat-rack returns a 200 OK and the
    correct 'Coat Rack' HTML fragment.
    """
    response = client.get("/set/add-coat-rack")
    assert response.status_code == 200
    assert 'data-testid="coat-rack-prop"' in response.text
    assert "Coat Rack" in response.text
    assert "🧥" in response.text

def test_get_props_inventory_returns_full_list_html():
    """
    Verifies that GET /props/inventory returns a 200 OK and the full
    HTML inventory, including the telephone that hx-select will target.
    """
    response = client.get("/props/inventory")
    assert response.status_code == 200
    assert 'id="inventory-list"' in response.text
    assert 'id="antique-telephone"' in response.text
    assert 'id="grandfather-clock"' in response.text
    assert "Antique Telephone" in response.text

def test_post_workshop_request_returns_confirmation_with_data():
    """
    Verifies that POST /workshop/request correctly processes form data
    and includes it in the 200 OK response.
    """
    # 1. Arrange: Define the form data to be sent.
    form_data = {"stage_width": "800", "stage_height": "600"}

    # 2. Act: Make the POST request with the data.
    response = client.post("/workshop/request", data=form_data)

    # 3. Assert: Check status and that the response contains the submitted data.
    assert response.status_code == 200
    assert 'data-testid="workshop-confirmation"' in response.text
    assert "Confirmed: New set piece ordered for stage (800x600)." in response.text

def test_get_cue_special_effects_returns_correct_header_and_body():
    """
    Verifies that GET /cue/special-effects returns a 200 OK, the correct
    HTML body, and the critical 'HX-Trigger' header.
    """
    response = client.get("/cue/special-effects")
    assert response.status_code == 200
    assert response.text == "<p>Effects cued!</p>"
    # This is the most important assertion for this test.
    assert "HX-Trigger" in response.headers
    assert response.headers["HX-Trigger"] == "flashLights, playSound"