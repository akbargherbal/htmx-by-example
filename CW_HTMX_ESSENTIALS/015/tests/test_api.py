# tests/test_api.py

# This file contains the API-level tests for our FastAPI application.
# The goal is to verify that each endpoint strictly adheres to the defined
# API contract, checking status codes, headers, and response bodies.
# We use FastAPI's TestClient, which provides a simple and effective way
# to make requests to the app without running a live server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup & Fixtures ---

# A pytest fixture with `autouse=True` is the gold standard for test setup.
# It automatically runs before every single test function in this file,
# guaranteeing a clean, isolated state for each test case. This prevents
# tests from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it doesn't need to be recreated for every test. The state isolation
# is handled by the `reset_state_before_each_test` fixture, not by
# re-creating the client.
client = TestClient(app)


# --- Test Functions ---

def test_post_request_book_success():
    """
    Verifies that POST /request-book correctly processes form data,
    returns a 200 OK status, includes the HX-Push-Url header, and
    renders the correct HTML fragment as per the API contract.
    """
    # 1. Arrange: Define the form data to be sent.
    form_data = {"title": "The Rare Tome", "author": "Jane Doe"}
    expected_slug = "the-rare-tome"

    # 2. Act: Make the POST request to the endpoint.
    response = client.post("/request-book", data=form_data)

    # 3. Assert: Verify every part of the contract's expected response.
    assert response.status_code == 200
    assert "Content-Type" in response.headers
    assert "text/html" in response.headers["Content-Type"]

    # Assert the critical HTMX header for deep linking.
    assert "HX-Push-Url" in response.headers
    assert response.headers["HX-Push-Url"] == f"/book/{expected_slug}"

    # Assert the content of the HTML fragment.
    assert "Request Fulfilled!" in response.text
    assert "The Rare Tome" in response.text
    assert "Jane Doe" in response.text
    assert f"/book/{expected_slug}" in response.text


def test_get_book_by_slug_after_post_success():
    """
    Verifies that a user can access a book's page directly via its slug
    (simulating a bookmark or direct navigation) after it has been created.
    This ensures the URL pushed by HTMX is a real, working endpoint.
    """
    # 1. Arrange: First, create the book state by calling the POST endpoint.
    # This is a valid way to set up state for a subsequent test.
    form_data = {"title": "The Rare Tome", "author": "Jane Doe"}
    client.post("/request-book", data=form_data)
    book_slug = "the-rare-tome"

    # 2. Act: Make a GET request to the newly available "deep link" URL.
    response = client.get(f"/book/{book_slug}")

    # 3. Assert: Verify the response is identical to the POST response fragment.
    assert response.status_code == 200
    assert "Content-Type" in response.headers
    assert "text/html" in response.headers["Content-Type"]

    # The GET endpoint should not set HTMX-specific headers.
    assert "HX-Push-Url" not in response.headers

    # Assert the content is correct, confirming state was read properly.
    assert "Request Fulfilled!" in response.text
    assert "The Rare Tome" in response.text
    assert "Jane Doe" in response.text
    assert f"/book/{book_slug}" in response.text


def test_get_root_returns_ok_and_html():
    """
    Verifies that the root endpoint (GET /) is available and serves
    an HTML page, which is the main entrypoint for the user.
    """
    # 1. Arrange: No arrangement needed for the root path.

    # 2. Act: Make a GET request to the root of the application.
    response = client.get("/")

    # 3. Assert: Check for a successful response and correct content type.
    assert response.status_code == 200
    assert "Content-Type" in response.headers
    assert "text/html" in response.headers["Content-Type"]