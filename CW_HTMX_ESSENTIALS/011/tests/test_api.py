# This file contains the API tests for the FastAPI application.
# As a Principal Engineer, I insist on tests that are clear, isolated, and
# directly verify the behavior defined in the API contract.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# This fixture is a cornerstone of reliable testing. By using `autouse=True`,
# it automatically runs before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state,
# eliminating dependencies between tests.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()


# We instantiate the TestClient once at the module level.
# This is efficient and provides a consistent interface for making requests
# to our FastAPI application within the tests.
client = TestClient(app)


# --- Test Functions ---

def test_get_inventory_returns_initial_list():
    """
    Verifies that GET /inventory returns a 200 OK and the initial inventory list.
    This test confirms the baseline state of the application is served correctly.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.get("/inventory")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    assert 'data-testid="inventory-item-wooden-sword"' in response.text
    assert 'data-testid="inventory-item-herbs"' in response.text
    assert "Wooden Sword" in response.text
    assert "Herbs" in response.text


def test_post_inventory_adds_item_and_returns_updated_list():
    """
    Verifies that POST /inventory correctly adds a new item and returns the
    full, updated list, highlighting the new item as per the contract.
    """
    # 1. Arrange & Act: Post form data to create a "Health Potion".
    response = client.post("/inventory", data={"itemName": "Health Potion"})

    # 2. Assert: Verify status, content, and the special highlight class.
    assert response.status_code == 200
    # Check that the new item is present and correctly formatted.
    assert 'data-testid="inventory-item-health-potion"' in response.text
    assert "Health Potion" in response.text
    # Check that the highlight class is applied to the new item.
    assert 'class="flex justify-between items-center bg-gray-700 p-3 rounded-md ring-2 ring-green-500"' in response.text
    # Check that the old items are still present.
    assert "Wooden Sword" in response.text
    assert "Herbs" in response.text


def test_put_equip_item_returns_equipped_slot_fragment():
    """
    Verifies that PUT /inventory/equip/{item_id} returns a 200 OK and the
    specific HTML fragment for the equipped item display.
    """
    # 1. Arrange & Act: Equip the "Wooden Sword" (ID 1).
    response = client.put("/inventory/equip/1")

    # 2. Assert: Verify the response is the correct fragment.
    assert response.status_code == 200
    assert 'id="equipped-item-slot"' in response.text
    assert "<strong>Equipped:</strong>" in response.text
    assert "Wooden Sword" in response.text
    # Ensure it's ONLY the fragment, not the whole inventory list.
    assert "Herbs" not in response.text


def test_delete_item_removes_it_and_returns_updated_list():
    """
    Verifies that DELETE /inventory/item/{item_id} removes the item and
    returns the updated inventory list without the deleted item.
    """
    # 1. Arrange & Act: Delete "Herbs" (ID 2).
    response = client.delete("/inventory/item/2")

    # 2. Assert: Verify the item is gone from the returned list.
    assert response.status_code == 200
    # The deleted item should not be in the response.
    assert 'data-testid="inventory-item-herbs"' not in response.text
    assert "Herbs" not in response.text
    # The remaining item should still be present.
    assert 'data-testid="inventory-item-wooden-sword"' in response.text
    assert "Wooden Sword" in response.text


def test_get_treasure_chest_returns_loot_container():
    """
    Verifies that GET /treasure-chest returns the full container of lootable items
    as specified in the contract, ready for the frontend to parse with hx-select.
    """
    # 1. Arrange & Act: Request the treasure chest contents.
    response = client.get("/treasure-chest")

    # 2. Assert: Verify the response contains all potential loot items.
    assert response.status_code == 200
    assert 'id="looted-sword"' in response.text
    assert 'data-testid="inventory-item-steel-sword"' in response.text
    assert "Steel Sword" in response.text
    assert 'id="looted-shield"' in response.text
    assert 'id="looted-helmet"' in response.text