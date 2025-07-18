# This file contains the API tests for our FastAPI application.
# The goal is to verify that each endpoint behaves exactly as defined in the API Contract.
# We use FastAPI's TestClient, which provides a simple and effective way to test the API
# without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This pytest fixture is a powerful feature that ensures a clean state for every test.
# The `autouse=True` argument tells pytest to run this fixture automatically before each
# test function, guaranteeing test isolation and preventing cascading failures.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level.
# This is efficient as it sets up the application wrapper only once for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_get_menu_item_soup_success():
    """
    Verifies that GET /menu-item?name=soup returns a 200 OK and the correct HTML fragment.
    This test directly validates the 'soup' case from the API contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/menu-item?name=soup")

    # 2. Assert: Verify the response against the API Contract.
    # Check the status code first, as it's the primary indicator of success.
    assert response.status_code == 200
    # Check for specific, unique text from the expected HTML to confirm the correct fragment was sent.
    assert "Soup of the Day" in response.text
    assert "Enjoy your hot and delicious soup!" in response.text
    # Verify the content-type header is correctly set for HTML.
    assert "text/html" in response.headers["content-type"]


def test_get_menu_item_special_success():
    """
    Verifies that GET /menu-item?name=special returns a 200 OK and the correct HTML fragment.
    This test directly validates the 'special' case from the API contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/menu-item?name=special")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert "Daily Special" in response.text
    assert "Perfectly grilled salmon with a side of asparagus." in response.text
    assert "text/html" in response.headers["content-type"]


def test_post_custom_order_success():
    """
    Verifies that POST /custom-order with form data returns a 200 OK and a
    dynamically generated HTML fragment confirming the order.
    """
    # 1. Arrange: Define the form data to be sent.
    # The TestClient requires the `data` payload to be a dictionary.
    # For fields with multiple values like checkboxes, pass a list of strings.
    form_data = {
        "toppings": ["Lettuce", "Cheese"],
        "special_requests": "extra pickles, toasted bun"
    }

    # 2. Act: Make the POST request with the form data.
    response = client.post("/custom-order", data=form_data)

    # 3. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert "Your Custom Burger is Ready!" in response.text
    # Check that the dynamic parts of the response were generated correctly.
    assert "<li>Lettuce</li>" in response.text
    assert "<li>Cheese</li>" in response.text
    assert "extra pickles, toasted bun" in response.text
    assert "text/html" in response.headers["content-type"]

def test_get_root_renders_html():
    """
    Verifies that the root path GET / serves the main HTML page.
    This is a basic sanity check to ensure the application entrypoint is working.
    """
    # 1. Arrange & Act
    response = client.get("/")

    # 2. Assert
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # A simple check for an expected element in the base HTML file.
    assert "<title>HTMX Restaurant</title>" in response.text