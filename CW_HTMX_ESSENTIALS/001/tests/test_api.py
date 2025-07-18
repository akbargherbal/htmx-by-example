# This file contains the API tests for our FastAPI application.
# The purpose of these tests is to verify, in isolation, that each API endpoint
# behaves exactly as specified in the API Contract. We are not testing the
# frontend here, only the server's responses.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, CHEF_STATUS_INITIAL

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. By decorating it with
# `autouse=True`, we ensure that our application's state is reset to a known,
# clean slate before every single test function is executed. This guarantees
# test isolation and prevents cascading failures.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This client simulates
# HTTP requests to our FastAPI application without needing to run a live server.
# It's fast, efficient, and perfect for API-level testing.
client = TestClient(app)


# --- Test Functions ---

def test_get_water_returns_correct_html_fragment():
    """
    Verifies that a GET request to /api/kitchen/water returns a 200 OK
    and the specific HTML fragment for a glass of water, as per the contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/api/kitchen/water")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type']
    assert "💧" in response.text
    assert "Here is your glass of water." in response.text

def test_add_recipe_returns_dynamic_html_fragment():
    """
    Verifies that a POST request to /api/kitchen/recipes with form data
    returns a 200 OK and an HTML fragment containing the submitted recipe name.
    """
    # 1. Arrange: Define the form data to be sent.
    recipe_data = {"recipeName": "Pesto Pasta"}

    # 2. Act: Make the POST request with the data.
    response = client.post("/api/kitchen/recipes", data=recipe_data)

    # 3. Assert: Check status, content type, and dynamic content.
    assert response.status_code == 200
    assert 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type']
    assert "📖" in response.text
    assert 'Recipe for "Pesto Pasta" added' in response.text

def test_adjust_soup_returns_correct_html_fragment():
    """
    Verifies that a PUT request to /api/kitchen/soup returns a 200 OK
    and the specific HTML fragment for seasoned soup.
    """
    # 1. Act: Make the PUT request.
    response = client.put("/api/kitchen/soup")

    # 2. Assert: Verify the response.
    assert response.status_code == 200
    assert 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type']
    assert "🍲" in response.text
    assert "The soup has been perfectly seasoned." in response.text

def test_discard_toast_returns_empty_body_with_200_ok():
    """
    Verifies that a DELETE request to /api/kitchen/toast returns a 200 OK
    status code and, crucially, an empty response body as per the contract.
    """
    # 1. Act: Make the DELETE request.
    response = client.delete("/api/kitchen/toast")

    # 2. Assert: Check status code and that the body is empty.
    assert response.status_code == 200
    assert response.text == ""

def test_get_chef_status_returns_initial_status():
    """
    Verifies that a GET request to /api/kitchen/chef-status returns a 200 OK
    and an HTML fragment containing the initial, default chef status.
    """
    # 1. Act: Make the GET request.
    response = client.get("/api/kitchen/chef-status")

    # 2. Assert: Verify the response contains the initial state.
    assert response.status_code == 200
    assert 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type']
    assert "<strong>Chef's Status:</strong>" in response.text
    assert CHEF_STATUS_INITIAL in response.text