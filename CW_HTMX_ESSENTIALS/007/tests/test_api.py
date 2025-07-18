# This file contains the API tests for our FastAPI application.
# The goal is to verify that each endpoint strictly adheres to its defined API contract.
# We test status codes, headers (implicitly via content-type), and the exact HTML response body.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, current_order

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. The `autouse=True` flag
# ensures it runs automatically before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state,
# preventing cascading failures and ensuring test isolation.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# Instantiate the TestClient once at the module level.
# This is more efficient than creating a new client for every test.
# The client simulates requests to the application without needing a live server.
client = TestClient(app)


# --- Test Cases for POST /add-item ---

def test_add_first_item_to_empty_order_succeeds():
    """
    Verifies that adding a single item to an empty order returns a 200 OK
    and an HTML fragment containing only that item. This is the "happy path" base case.
    """
    # Arrange: The `reset_state_before_each_test` fixture ensures the order is empty.
    # Act: Simulate a form submission to the /add-item endpoint.
    response = client.post("/add-item", data={"item": "Cheeseburger", "quantity": "2"})

    # Assert: Verify the response against the API contract.
    assert response.status_code == 200
    # We check for the specific list item HTML to confirm the data was processed correctly.
    assert '<li>2 x Cheeseburger</li>' in response.text
    # We also ensure the server state was correctly updated.
    assert len(current_order) == 1
    assert current_order[0].name == "Cheeseburger"
    assert current_order[0].quantity == 2

def test_add_second_distinct_item_returns_full_list():
    """
    Verifies that after one item is already in the order, adding a second,
    different item returns an HTML fragment containing both items.
    """
    # Arrange: Add an initial item to the order.
    client.post("/add-item", data={"item": "Cheeseburger", "quantity": "1"})

    # Act: Add a second, different item.
    response = client.post("/add-item", data={"item": "Fries", "quantity": "1"})

    # Assert: The response should now contain both items.
    assert response.status_code == 200
    assert '<li>1 x Cheeseburger</li>' in response.text
    assert '<li>1 x Fries</li>' in response.text
    # Verify the underlying server state is also correct.
    assert len(current_order) == 2

def test_add_existing_item_updates_quantity_correctly():
    """
    Verifies that posting an item that already exists in the order updates
    the quantity of the existing item rather than creating a duplicate entry.
    """
    # Arrange: Add an initial item.
    client.post("/add-item", data={"item": "Soda", "quantity": "1"})

    # Act: Add the *same* item again, but with a different quantity.
    response = client.post("/add-item", data={"item": "Soda", "quantity": "2"})

    # Assert: The response should show a single entry with the combined quantity.
    assert response.status_code == 200
    assert '<li>3 x Soda</li>' in response.text
    # Crucially, ensure no new item was added to the list.
    assert len(current_order) == 1
    assert current_order[0].quantity == 3

def test_add_item_with_invalid_quantity_fails_validation():
    """
    Verifies that the endpoint correctly rejects requests where the 'quantity'
    is not a valid integer. This tests FastAPI's built-in validation.
    A 422 Unprocessable Entity is the correct, expected response for this failure.
    """
    # Act: Attempt to post a non-integer quantity.
    response = client.post("/add-item", data={"item": "Salad", "quantity": "invalid"})

    # Assert: The request should be rejected before our handler logic is even called.
    assert response.status_code == 422