# This file contains the API tests for our FastAPI application.
# As a Principal Engineer, I insist on a test-driven approach. These tests
# verify that each endpoint strictly adheres to the defined API Contract.
# We use FastAPI's TestClient, which provides a simple and efficient way
# to make requests to the application in-memory, without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. The `autouse=True` argument
# ensures it runs automatically before every single test function. By calling
# `reset_state_for_testing()`, we guarantee that each test starts with a
# clean, predictable state, eliminating inter-test dependencies.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it doesn't need to be recreated for every test. The client wraps our
# FastAPI `app` object, allowing us to make requests to it programmatically.
client = TestClient(app)


# --- Test Functions ---

def test_register_success_returns_200_and_confirmation_html():
    """
    Verifies that POST /register/success correctly returns a 200 OK status
    and the HTML fragment for a successful registration, as per the contract.
    """
    # 1. Arrange & Act: Make the POST request to the target endpoint.
    response = client.post("/register/success")

    # 2. Assert: Verify the three key parts of the response.
    # Status code must be 200 OK.
    assert response.status_code == 200
    # The response body must contain the specific success message and data-testid.
    assert 'data-testid="main-content-after-success"' in response.text
    assert "You have successfully registered" in response.text
    assert "BIOL-101: Introduction to Biology" in response.text

def test_register_full_returns_409_and_error_html():
    """
    Verifies that POST /register/full returns a 409 Conflict status
    and the HTML fragment for a "course full" error.
    """
    # 1. Arrange & Act
    response = client.post("/register/full")

    # 2. Assert
    # Status code must be 409 Conflict.
    assert response.status_code == 409
    # The response body must contain the specific error message and data-testid.
    assert 'data-testid="registration-error-target-after-action"' in response.text
    assert "Error: Course is full." in response.text

def test_get_grades_forbidden_returns_403_and_access_denied_html():
    """
    Verifies that GET /records/grades/forbidden returns a 403 Forbidden status
    and the HTML fragment for an "access denied" error.
    """
    # 1. Arrange & Act
    response = client.get("/records/grades/forbidden")

    # 2. Assert
    # Status code must be 403 Forbidden.
    assert response.status_code == 403
    # The response body must contain the specific error message and data-testid.
    assert 'data-testid="records-result-target-after-403"' in response.text
    assert "Access Denied (403 Forbidden)" in response.text

def test_get_transcript_not_found_returns_404_and_not_found_html():
    """
    Verifies that GET /records/transcript/not-found returns a 404 Not Found status
    and the HTML fragment for a "not found" error.
    """
    # 1. Arrange & Act
    response = client.get("/records/transcript/not-found")

    # 2. Assert
    # Status code must be 404 Not Found.
    assert response.status_code == 404
    # The response body must contain the specific error message and data-testid.
    assert 'data-testid="records-result-target-after-404"' in response.text
    assert "The requested transcript for the specified student ID does not exist." in response.text

def test_get_grades_payment_due_returns_200_and_hx_redirect_header():
    """
    Verifies that GET /records/grades/payment-due returns a 200 OK status,
    an empty body, and the critical HX-Redirect header pointing to /pay-tuition.
    """
    # 1. Arrange & Act
    response = client.get("/records/grades/payment-due")

    # 2. Assert
    # Status code must be 200 OK, as the request itself was successful.
    assert response.status_code == 200
    # The key assertion: the HX-Redirect header must be present and correct.
    assert response.headers["HX-Redirect"] == "/pay-tuition"
    # The body should be empty as it's ignored by HTMX during a redirect.
    assert response.text == ""

def test_get_pay_tuition_returns_200_and_payment_page_html():
    """
    Verifies that the redirect target, GET /pay-tuition, returns a 200 OK
    status and the correct HTML for the payment page.
    """
    # 1. Arrange & Act
    response = client.get("/pay-tuition")

    # 2. Assert
    # Status code must be 200 OK.
    assert response.status_code == 200
    # The response body must contain the specific content for the redirect page.
    assert 'data-testid="main-content-after-redirect"' in response.text
    assert "Tuition Payment Required" in response.text
    assert "Pay Tuition Now" in response.text