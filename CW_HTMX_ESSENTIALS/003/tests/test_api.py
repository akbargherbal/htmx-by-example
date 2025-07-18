# This file contains the API tests for our FastAPI application.
# The goal is to verify that each endpoint behaves exactly as defined in the API Contract.
# We use FastAPI's TestClient, which provides a simple and efficient way to make
# requests to the application without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# This fixture is a cornerstone of reliable testing. By decorating it with
# `autouse=True`, we ensure that our application's state is reset to a known,
# clean baseline before every single test function is executed. This prevents
# tests from interfering with each other and guarantees test isolation.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient as it
# sets up the client a single time for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_get_exhibit_returns_correct_html_fragment():
    """
    Verifies that GET /exhibit/{slug} returns a 200 OK and the correct HTML
    fragment for a valid exhibit, as specified in the API contract.
    """
    # 1. Arrange & Act: Make a request to a specific exhibit endpoint.
    response = client.get("/exhibit/impressionism")

    # 2. Assert: Verify the response against the contract.
    # Check the status code.
    assert response.status_code == 200
    # Check for key content in the HTML body. This confirms the correct data was used.
    assert "Exhibit: Impressionism" in response.text
    assert "19th-century art movement" in response.text
    # Verify that the dynamic path is correctly included in the response.
    assert '<code>/exhibit/impressionism</code>' in response.text

def test_post_request_from_archives_returns_retrieved_piece_html():
    """
    Verifies that POST /request-from-archives returns a 200 OK and the HTML
    fragment confirming the retrieval of an archived piece.
    """
    # 1. Arrange & Act: Make the POST request.
    response = client.post("/request-from-archives")

    # 2. Assert: Verify the response.
    assert response.status_code == 200
    # Check for the specific content defined in the contract.
    assert "Retrieved:" in response.text
    assert "'The Starry Night' by Vincent van Gogh" in response.text
    # Ensure the container div is present.
    assert 'data-testid="archive-content-area"' in response.text

def test_delete_move_sculpture_returns_success_html():
    """
    Verifies that DELETE /move-sculpture returns a 200 OK and the HTML
    fragment showing the success message and the disabled button.
    """
    # 1. Arrange & Act: Make the DELETE request.
    response = client.delete("/move-sculpture")

    # 2. Assert: Verify the response.
    assert response.status_code == 200
    # Check for the success message and details.
    assert "Success! Sculpture:</span> &#x27;The Thinker&#x27;" in response.text # Note: HTML encoding of '
    assert "New Location: West Garden" in response.text
    # Crucially, verify that the button is now returned in a 'disabled' state.
    assert "disabled>Moved</button>" in response.text