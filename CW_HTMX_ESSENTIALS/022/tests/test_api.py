# This file contains the API tests for the FastAPI application.
# As a Principal Engineer, I emphasize that API tests are the foundation of a reliable
# system. They verify the contract between the frontend and backend, ensuring that
# each endpoint behaves exactly as expected regarding status codes, headers, and
# response bodies.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, GARDEN_STATE

# This pytest fixture is a powerful pattern. By setting `autouse=True`, it
# automatically runs before every single test function in this file. This
# guarantees that each test starts with a clean, predictable state,
# preventing tests from interfering with each other.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# and provides a consistent interface for making requests to our app in tests.
client = TestClient(app)


# --- Test Functions ---

def test_post_garden_plots_creates_new_plant():
    """
    Verifies that POST /garden/plots correctly creates a new plant,
    updates the server state, and returns the correct HTML fragment.
    """
    # 1. Arrange: Define the new plant's name.
    plant_name = "Basil"
    normalized_name = "basil"

    # 2. Act: Make the POST request, simulating a form submission.
    response = client.post("/garden/plots", data={"plant_name": plant_name})

    # 3. Assert: Verify the response and the resulting state.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    # Check that the response body contains the expected HTML structure and content.
    assert f'data-testid="plant-plot-{normalized_name}"' in response.text
    assert f"🌱 {plant_name}" in response.text
    # Verify that the application state was actually updated on the backend.
    assert GARDEN_STATE["plots"][3] == plant_name


def test_put_garden_plots_replaces_existing_plant():
    """
    Verifies that PUT /garden/plots/{plot_id} correctly replaces an existing
    plant and returns the updated HTML fragment as per the API contract.
    """
    # 1. Arrange: The initial state (from the fixture) has a "Tomato" at plot_id=1.
    plot_id_to_replace = 1

    # 2. Act: Make the PUT request to the specific plot's endpoint.
    response = client.put(f"/garden/plots/{plot_id_to_replace}")

    # 3. Assert: Verify the response and state change.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    # The contract specifies it's replaced with a "Carrot".
    assert 'data-testid="plant-plot-carrot"' in response.text
    assert "🥕 Carrot" in response.text
    # Verify the backend state was updated.
    assert GARDEN_STATE["plots"][plot_id_to_replace] == "Carrot"


def test_delete_garden_plots_removes_plant():
    """
    Verifies that DELETE /garden/plots/{plot_id} successfully removes a plot
    and returns an empty 200 OK response, which is the signal for HTMX to
    remove the element from the DOM.
    """
    # 1. Arrange: The initial state has a "Weed" at plot_id=2.
    plot_id_to_delete = 2
    assert plot_id_to_delete in GARDEN_STATE["plots"]

    # 2. Act: Make the DELETE request.
    response = client.delete(f"/garden/plots/{plot_id_to_delete}")

    # 3. Assert: Verify the response and state change.
    assert response.status_code == 200
    # The contract specifies an empty body for a successful deletion.
    assert response.text == ""
    # Verify the plot was actually removed from the backend state.
    assert plot_id_to_delete not in GARDEN_STATE["plots"]


def test_get_garden_status_when_weeds_present():
    """
    Verifies that GET /garden/status returns the 'Needs Weeding' message
    when the initial state (which contains a weed) is present.
    """
    # 1. Arrange: The `reset_state_before_each_test` fixture ensures a weed exists.

    # 2. Act: Make the GET request to the status endpoint.
    response = client.get("/garden/status")

    # 3. Assert: Verify the correct status message and styling classes are returned.
    assert response.status_code == 200
    assert "🚨 Needs Weeding" in response.text
    assert 'class="mt-2 bg-red-900/50 p-4 rounded-lg border border-red-700"' in response.text


def test_get_garden_status_when_garden_is_clean():
    """
    Verifies that GET /garden/status returns the 'Thriving' message after
    any weeds have been removed from the garden.
    """
    # 1. Arrange: First, remove the weed from the initial state.
    client.delete("/garden/plots/2")

    # 2. Act: Now, make the GET request to the status endpoint.
    response = client.get("/garden/status")

    # 3. Assert: Verify the 'thriving' status is returned.
    assert response.status_code == 200
    assert "✨ Garden is Thriving" in response.text
    assert 'class="mt-2 bg-green-900/50 p-4 rounded-lg border border-green-700"' in response.text