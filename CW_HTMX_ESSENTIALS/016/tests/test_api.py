# This file contains the API tests for our FastAPI application.
# The primary goal is to verify that each endpoint strictly adheres to the
# defined API contract, checking status codes, headers, and response bodies.
# Test-Driven Development (TDD) is a best practice for building reliable systems.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup & Fixtures ---

# The `autouse=True` argument ensures this fixture is automatically run before
# every single test function in this file. This is the cornerstone of test
# isolation, guaranteeing a clean slate for each test case.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset application state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is efficient
# as it doesn't need to be recreated for every test. The client simulates
# HTTP requests to our FastAPI application in memory.
client = TestClient(app)


# --- Test Cases ---

def test_get_root_serves_main_html_page():
    """
    Verifies that the root path (GET /) successfully returns a 200 OK
    and the main HTML content, ensuring the application entrypoint is working.
    """
    # 1. Arrange & Act: Make the request to the root endpoint.
    response = client.get("/")

    # 2. Assert: Verify the response is a valid, complete HTML page.
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # A simple check to ensure it's the main page, not just a fragment.
    assert "<html>" in response.text
    assert "Product Catalog" in response.text

def test_get_products_t_shirts_returns_correct_fragment():
    """
    Verifies that GET /products/t-shirts returns a 200 OK and the specific
    HTML fragment for T-shirts, as defined in the API contract.
    """
    # 1. Arrange & Act
    response = client.get("/products/t-shirts")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'HTMX Logo Tee' in response.text
    assert '"I Use Arch" Tee' in response.text
    assert '$32.00' in response.text

def test_get_products_hats_returns_correct_fragment():
    """
    Verifies that GET /products/hats returns a 200 OK and the specific
    HTML fragment for hats, as defined in the API contract.
    """
    # 1. Arrange & Act
    response = client.get("/products/hats")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'Classic Snapback' in response.text
    assert 'Winter Beanie' in response.text
    assert '$22.00' in response.text

def test_post_checkout_process_returns_success_message():
    """
    Verifies that POST /checkout/process returns a 200 OK and the
    'order placed' success message fragment, as per the API contract.
    """
    # 1. Arrange & Act
    response = client.post("/checkout/process")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "✓ Order placed successfully!" in response.text