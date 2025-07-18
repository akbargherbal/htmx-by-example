# This file contains the API tests for our FastAPI application.
# As a Principal Engineer, I insist on tests that are readable, isolated, and
# precisely verify the behavior defined in the API contract.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, HEADLINES, BREAKING_STORY

# This fixture is the cornerstone of reliable testing. By using `autouse=True`,
# it automatically runs before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level.
# This is efficient and provides a consistent interface for making requests to our app in tests.
client = TestClient(app)


# --- Test Functions ---

def test_read_root_serves_initial_state():
    """
    Verifies that the root path (GET /) successfully serves the main HTML page
    and that the initial server state is correctly rendered in the template.
    """
    # 1. Arrange & Act: Make the request to the root endpoint.
    response = client.get("/")

    # 2. Assert: Verify the response against the contract.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check for the initial message passed from the server state to the template.
    assert "System Initialized" in response.text

def test_get_headlines_cycles_through_list():
    """
    Verifies that GET /api/headlines correctly cycles through the predefined list
    of headlines and returns the expected HTML fragment.
    """
    # 1. Arrange & Act: Call the endpoint N+1 times, where N is the number of headlines.
    # This ensures we test the wrap-around behavior of the cycle.
    responses = [client.get("/api/headlines") for _ in range(len(HEADLINES) + 1)]

    # 2. Assert: Check status codes and content.
    for response in responses:
        assert response.status_code == 200
        assert '<p class="text-sm">' in response.text

    # Verify that the first headline appears as both the first and last response.
    response_texts = [r.text for r in responses]
    assert HEADLINES[0] in response_texts[0]
    assert HEADLINES[0] in response_texts[-1]

def test_post_broadcast_alert_returns_trigger_header():
    """
    Verifies that POST /api/broadcast/alert returns a 200 OK status, an empty body,
    and the critical HX-Trigger header as specified in the API contract.
    """
    # 1. Arrange & Act
    response = client.post("/api/broadcast/alert")

    # 2. Assert
    assert response.status_code == 200
    assert response.headers["HX-Trigger"] == "newBreakingNews"
    assert response.text == ""  # The body must be empty.

def test_get_breaking_story_returns_correct_html():
    """
    Verifies that GET /api/story/breaking returns a 200 OK status and the
    correct HTML fragment for the breaking news story.
    """
    # 1. Arrange & Act
    response = client.get("/api/story/breaking")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "BREAKING NEWS" in response.text
    assert BREAKING_STORY in response.text

def test_post_coordinated_update_returns_main_and_oob_fragments():
    """
    Verifies that POST /api/broadcast/coordinated-update returns a single response
    that contains both the main content and a correctly formatted Out-of-Band fragment.
    """
    # 1. Arrange & Act
    response = client.post("/api/broadcast/coordinated-update")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Assert that the main fragment content is present.
    assert "BREAKING NEWS" in response.text
    assert BREAKING_STORY in response.text

    # Assert that the OOB fragment is correctly structured.
    assert 'id="alerts-sidebar-list" hx-swap-oob="true"' in response.text

    # Assert that the new alert content is in the OOB fragment.
    assert "Coordinated Update Received" in response.text

    # Crucially, assert that the initial state is also present, proving
    # that the server correctly updated its state and returned the full list.
    assert "System Initialized" in response.text