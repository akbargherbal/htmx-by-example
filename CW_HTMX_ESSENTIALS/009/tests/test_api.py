# This file contains API-level tests for the FastAPI application.
# It uses fastapi.testclient.TestClient to make requests directly to the
# application without needing a running server. This is efficient and reliable
# for verifying API contracts.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, ITEMS, credit as app_credit

# This fixture is a cornerstone of reliable testing. It uses `autouse=True`
# to automatically run before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state,
# preventing tests from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level. This is more
# efficient than creating a new client for every test.
client = TestClient(app)


# --- Test Functions ---

def test_get_item_info_success():
    """
    Verifies that GET /item-info/{item_id} returns a 200 OK and the correct
    HTML fragment with item details, as per the API contract.
    """
    # Arrange: Define the item we want to query.
    item_id = "A1"
    expected_item = ITEMS[item_id]

    # Act: Make the request to the endpoint.
    response = client.get(f"/item-info/{item_id}")

    # Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    # Check for key pieces of information in the returned HTML.
    assert f"{item_id}: {expected_item.name}" in response.text
    assert f"Calories: {expected_item.calories}" in response.text
    assert f"Sodium: {expected_item.sodium}mg" in response.text

def test_add_credit_success():
    """
    Verifies that POST /add-credit returns a 200 OK and the two required
    HTML fragments: the updated item grid and the OOB credit display.
    """
    # Arrange: The initial credit is $0.00. After one call, it should be $0.25.
    initial_credit = app_credit
    assert initial_credit == 0.0

    # Act: Make the request to the endpoint.
    response = client.post("/add-credit")

    # Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    # Assert on the main fragment (the re-rendered item grid).
    assert 'id="item-grid-container"' in response.text
    # Initially, A1 ($0.75) is unaffordable. After adding credit, it should still be.
    assert 'data-testid="item_selection_button-A1-unaffordable"' in response.text

    # Assert on the OOB fragment (the updated credit display).
    assert 'id="credit-display" hx-swap-oob="innerHTML"' in response.text
    assert "$0.25" in response.text

def test_purchase_item_success():
    """
    Verifies that a successful purchase returns a 200 OK with two OOB fragments
    for updating the credit and the retrieval bin, and an empty main body.
    """
    # Arrange: We need enough credit to buy the item. Let's add credit 3 times.
    client.post("/add-credit") # 0.25
    client.post("/add-credit") # 0.50
    client.post("/add-credit") # 0.75 -> now we can afford A1
    item_id_to_purchase = "A1"
    item_name = ITEMS[item_id_to_purchase].name

    # Act: Make the purchase request.
    response = client.post(f"/purchase/{item_id_to_purchase}")

    # Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

    # Assert that the credit display OOB fragment is present and correct ($0.75 - $0.75 = $0.00).
    assert 'id="credit-display" hx-swap-oob="innerHTML"' in response.text
    assert "$0.00" in response.text

    # Assert that the retrieval bin OOB fragment is present and correct.
    assert 'id="retrieval-bin-target" hx-swap-oob="beforeend"' in response.text
    assert item_name in response.text

def test_purchase_sold_out_item_fails_with_404():
    """
    Verifies that attempting to purchase a sold-out item returns a 404 Not Found
    with the specific "SOLD OUT" error message, as per the API contract.
    """
    # Arrange: Add enough credit to afford the sold-out item, to ensure the
    # failure is due to stock, not funds. Item B2 costs $1.25.
    for _ in range(5):
        client.post("/add-credit") # 5 * 0.25 = 1.25
    
    sold_out_item_id = "B2"
    assert ITEMS[sold_out_item_id].stock == 0 # Verify precondition

    # Act: Attempt to purchase the sold-out item.
    response = client.post(f"/purchase/{sold_out_item_id}")

    # Assert: Verify the response against the API Contract.
    assert response.status_code == 404
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "SOLD OUT" in response.text
    assert f"Item {sold_out_item_id} is unavailable" in response.text