# This file contains the API tests for our FastAPI application.
# As a Principal Engineer, I insist on tests that are readable, isolated,
# and directly verify the API contract. We use FastAPI's TestClient, which
# provides a simple and effective way to make requests to our app in-memory.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, device_state

# This fixture is a cornerstone of reliable testing. By marking it with
# `autouse=True`, we ensure that our application's state is reset to a known,
# clean slate before every single test function runs. This prevents tests
# from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it doesn't need to be recreated for every test. The client simulates
# HTTP requests to our FastAPI application.
client = TestClient(app)


# --- Test Functions ---

def test_get_root_serves_html_page():
    """
    Verifies that the root path (GET /) successfully returns a 200 OK
    and that the response is HTML. This confirms the main application
    page is being served correctly.
    """
    # 1. Arrange & Act: Make the request to the root endpoint.
    response = client.get("/")

    # 2. Assert: Verify the response against the contract.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # A simple check to ensure it's not an empty page.
    assert "<h1>Smart Home Dashboard</h1>" in response.text

def test_get_all_status_returns_combined_html():
    """
    Verifies that GET /all-status returns a 200 OK and the combined HTML
    for all three devices based on the initial state.
    """
    # 1. Arrange & Act
    response = client.get("/all-status")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for key identifiers from each component's HTML.
    assert "Living Room Speaker" in response.text
    assert "90s Rock Anthems" in response.text
    assert "Kitchen Light" in response.text
    assert "Status: <span class=\"font-bold text-green-400\">On</span>" in response.text
    assert "Ambient Temperature" in response.text
    assert "22°C" in response.text

def test_post_playlist_updates_state_and_returns_speaker_html():
    """
    Verifies that POST /playlist correctly updates the playlist name and
    returns only the updated HTML fragment for the speaker.
    """
    # 1. Arrange: Define the new playlist data.
    new_playlist = "Synthwave Hits"
    form_data = {"playlistName": new_playlist}

    # 2. Act: Make the POST request with the form data.
    response = client.post("/playlist", data=form_data)

    # 3. Assert: Verify the response and the state change.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # The response should contain the new playlist name.
    assert f"Playlist: <span class=\"font-mono text-green-300\">{new_playlist}</span>" in response.text
    # The response should NOT contain HTML for other components.
    assert "Kitchen Light" not in response.text
    # Also, assert that the underlying state was actually mutated.
    assert device_state["speaker"]["playlist"] == new_playlist

def test_post_toggle_light_switches_from_on_to_off():
    """
    Verifies that POST /toggle-light switches the light from its initial
    'On' state to 'Off' and returns the correct HTML fragment.
    """
    # 1. Arrange: The initial state is 'On' due to the reset fixture.
    
    # 2. Act: Make the first POST request to toggle the light.
    response = client.post("/toggle-light")

    # 3. Assert: Verify the light is now 'Off'.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Status: <span class=\"font-bold text-red-400\">Off</span>" in response.text
    # Check for the 'Off' state CSS class.
    assert "ring-gray-600" in response.text
    # Verify the underlying state was mutated.
    assert device_state["light"]["is_on"] is False

def test_post_toggle_light_switches_from_off_to_on():
    """
    Verifies that a second POST to /toggle-light switches the light
    from 'Off' back to 'On'.
    """
    # 1. Arrange: First, toggle the light to the 'Off' state.
    client.post("/toggle-light")
    assert device_state["light"]["is_on"] is False # Sanity check

    # 2. Act: Make the second POST request to toggle it back.
    response = client.post("/toggle-light")

    # 3. Assert: Verify the light is now 'On' again.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Status: <span class=\"font-bold text-green-400\">On</span>" in response.text
    # Check for the 'On' state CSS class.
    assert "ring-yellow-400" in response.text
    # Verify the underlying state was mutated back.
    assert device_state["light"]["is_on"] is True

def test_get_temperature_returns_correct_html():
    """
    Verifies that GET /temperature returns a 200 OK and the correct
    HTML fragment for the temperature component.
    """
    # 1. Arrange & Act
    response = client.get("/temperature")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Ambient Temperature" in response.text
    assert "22°C" in response.text
    # Ensure it only returns the temperature component.
    assert "Living Room Speaker" not in response.text