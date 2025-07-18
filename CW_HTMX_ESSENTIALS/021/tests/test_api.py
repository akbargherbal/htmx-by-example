# tests/test_api.py

# This file contains the API-level tests for our FastAPI application.
# The goal is to verify that each endpoint behaves exactly as defined in the
# API contract, checking status codes, headers, and response bodies.
# We use FastAPI's TestClient, which provides a simple and effective way
# to make requests to the application in a testing context.

import pytest
from fastapi.testclient import TestClient
from app.main import app, APP_STATE, reset_state_for_testing

# --- Test Setup ---

# PRINCIPLE: For test isolation, we must reset the application's state before
# every single test. The `autouse=True` argument tells pytest to run this
# fixture automatically for every test function, eliminating boilerplate and
# preventing state from one test from leaking into another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it doesn't need to be recreated for every test.
client = TestClient(app)


# --- Test Cases for API Contract ---

def test_login_succeeds_when_card_is_inserted():
    """
    Verifies that POST /login returns 200 OK and an auth success message
    when the 'card_inserted' state is true.
    """
    # Arrange: Set the precondition for a successful login.
    APP_STATE["card_inserted"] = True
    APP_STATE["balance"] = 1000.00

    # Act: Make the request to the login endpoint.
    response = client.post("/login", data={"pin": "1234"})

    # Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert "Authentication Successful!" in response.text
    assert "Current Balance: $1000.00" in response.text
    # Also assert that the internal state was correctly updated.
    assert APP_STATE["authenticated"] is True

def test_login_fails_when_no_card_is_inserted():
    """
    Verifies that POST /login returns 402 Payment Required when the
    'card_inserted' state is false, as per the contract.
    """
    # Arrange: The default state has card_inserted = False, so no setup is needed.

    # Act: Make the request to the login endpoint.
    response = client.post("/login", data={"pin": "1234"})

    # Assert: Verify the specific error response.
    assert response.status_code == 402
    assert "Error: No Card Inserted" in response.text
    assert APP_STATE["authenticated"] is False

def test_withdraw_succeeds_with_sufficient_funds():
    """
    Verifies that POST /withdraw returns 200 OK and the new balance
    when the withdrawal amount is less than or equal to the current balance.
    """
    # Arrange: Set a known balance to test against.
    APP_STATE["balance"] = 500.00

    # Act: Attempt a valid withdrawal.
    response = client.post("/withdraw", data={"amount": "200"})

    # Assert: Check for the success message and correct new balance.
    assert response.status_code == 200
    assert "Withdrawal Successful!" in response.text
    assert "New Balance: $300.00" in response.text
    # Verify the state was correctly mutated.
    assert APP_STATE["balance"] == 300.00

def test_withdraw_fails_with_insufficient_funds():
    """
    Verifies that POST /withdraw returns 403 Forbidden when the withdrawal
    amount is greater than the current balance.
    """
    # Arrange: Set a balance that is lower than the withdrawal amount.
    APP_STATE["balance"] = 100.00

    # Act: Attempt an invalid withdrawal.
    response = client.post("/withdraw", data={"amount": "200"})

    # Assert: Check for the specific error message and status code.
    assert response.status_code == 403
    assert "Transaction Failed: Insufficient Funds" in response.text
    assert "Attempted to withdraw $200.00" in response.text
    assert "balance is only $100.00" in response.text
    # Verify the state was not mutated.
    assert APP_STATE["balance"] == 100.00

def test_check_balance_succeeds_when_authenticated():
    """
    Verifies that GET /balance returns 200 OK and the balance HTML fragment
    when the user session is authenticated.
    """
    # Arrange: Set the authenticated state and a known balance.
    APP_STATE["authenticated"] = True
    APP_STATE["balance"] = 1234.56

    # Act: Request the balance.
    response = client.get("/balance")

    # Assert: Check for the correct status, content, and absence of redirect header.
    assert response.status_code == 200
    assert "Your current balance is: $1234.56" in response.text
    assert "hx-redirect" not in response.headers

def test_check_balance_redirects_when_not_authenticated():
    """
    Verifies that GET /balance returns 200 OK with an HX-Redirect header
    when the user session is not authenticated.
    """
    # Arrange: The default state is not authenticated.

    # Act: Request the balance.
    response = client.get("/balance")

    # Assert: Check for the 200 status and the presence/value of the redirect header.
    assert response.status_code == 200
    assert "hx-redirect" in response.headers
    assert response.headers["hx-redirect"] == "/home"
    # The body should be empty as per the contract (N/A).
    assert response.text == ""

def test_get_home_returns_correct_content():
    """
    Verifies that GET /home returns the specified informational message,
    as it is the target of the client-side redirect.
    """
    # Arrange: No state setup needed for this static endpoint.

    # Act: Request the /home URL directly.
    response = client.get("/home")

    # Assert: Check for the correct content.
    assert response.status_code == 200
    assert "Please insert your card and enter your PIN" in response.text

def test_read_root_serves_html_page():
    """
    Verifies that the root GET / endpoint successfully serves an HTML page.
    This is a basic sanity check for the application entrypoint.
    """
    # Arrange: No setup needed.

    # Act: Request the root of the application.
    response = client.get("/")

    # Assert: Check for a successful response and the correct content type.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]