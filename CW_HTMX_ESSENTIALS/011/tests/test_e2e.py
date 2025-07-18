# Principal Engineer's Note:
# This file contains the end-to-end (E2E) tests for the inventory system.
# E2E tests are the ultimate proof that the frontend and backend are correctly integrated.
# We use Playwright to simulate real user actions in a browser.
# Each test follows the Arrange-Act-Assert pattern and uses `data-testid` selectors
# for maximum resilience against cosmetic HTML changes. Assertions use Playwright's `expect`
# for its powerful auto-waiting and expressive syntax.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_initial_page_load_shows_correct_state(page: Page, live_server):
    """
    Verifies that the initial page loads correctly, displaying the default
    inventory and the correct "nothing equipped" status.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Verify the initial state of the UI.
    # Check that the initial inventory items are visible.
    expect(page.get_by_test_id("inventory-item-wooden-sword")).to_be_visible()
    expect(page.get_by_test_id("inventory-item-herbs")).to_be_visible()

    # Check that the equipped item slot shows "Nothing".
    equipped_slot = page.get_by_test_id("equipped-item-slot")
    expect(equipped_slot).to_contain_text("Equipped: Nothing")


def test_craft_item_adds_it_to_inventory_with_highlight(page: Page, live_server):
    """
    Tests the complete POST flow: filling the form, clicking "Craft", and
    verifying the new item appears in the list with the correct highlight.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user crafting a "Health Potion".
    page.get_by_test_id("craft-input").fill("Health Potion")
    page.get_by_test_id("craft-button").click()

    # 3. Assert: Verify the UI has updated correctly.
    new_item = page.get_by_test_id("inventory-item-health-potion")
    expect(new_item).to_be_visible()
    expect(new_item).to_contain_text("Health Potion")

    # Crucially, verify the backend's response included the highlight class.
    # This confirms we are testing against the true backend behavior.
    expect(new_item).to_have_class(
        "flex justify-between items-center bg-gray-700 p-3 rounded-md ring-2 ring-green-500"
    )

    # Also assert that the input field was cleared after the request.
    expect(page.get_by_test_id("craft-input")).to_have_value("")


def test_drop_item_removes_it_from_inventory(page: Page, live_server):
    """
    Tests the DELETE flow: clicking a "Drop" button and verifying the
    item is removed from the DOM.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")
    item_to_drop = page.get_by_test_id("inventory-item-herbs")
    expect(item_to_drop).to_be_visible() # Confirm it exists before dropping.

    # Set up a handler to automatically accept the confirmation dialog.
    page.on("dialog", lambda dialog: dialog.accept())

    # 2. Act: Click the drop button for "Herbs".
    page.get_by_test_id("drop-button-herbs").click()

    # 3. Assert: The item is no longer in the inventory list.
    expect(item_to_drop).not_to_be_visible()
    # Verify other items remain.
    expect(page.get_by_test_id("inventory-item-wooden-sword")).to_be_visible()


def test_equip_item_updates_equipped_slot(page: Page, live_server):
    """
    Tests the PUT flow: clicking an "Equip" button and verifying the
    "Equipped Item Slot" is updated with the correct item name.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")
    equipped_slot = page.get_by_test_id("equipped-item-slot")
    expect(equipped_slot).to_contain_text("Nothing") # Verify initial state.

    # 2. Act: Click the equip button for "Wooden Sword".
    page.get_by_test_id("equip-button-wooden-sword").click()

    # 3. Assert: The equipped slot now displays "Wooden Sword".
    expect(equipped_slot).to_contain_text("Equipped: Wooden Sword")
    # Verify the text color, which is part of the backend's HTML fragment.
    expect(equipped_slot.get_by_text("Wooden Sword")).to_have_class("font-mono text-xl text-cyan-300")


def test_loot_chest_adds_only_selected_item_to_inventory(page: Page, live_server):
    """
    Tests the hx-select feature: clicking "Loot" should fetch a block of HTML
    but only append the selected item (#looted-sword) to the inventory.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the loot button.
    page.get_by_test_id("loot-button").click()

    # 3. Assert: The "Steel Sword" is now in the inventory.
    looted_item = page.get_by_test_id("inventory-item-steel-sword")
    expect(looted_item).to_be_visible()
    expect(looted_item).to_contain_text("Steel Sword")

    # Assert that other items from the treasure chest response were NOT added.
    # This proves hx-select worked correctly.
    expect(page.get_by_test_id("inventory-item-iron-shield", exact=True)).not_to_be_visible()
    expect(page.get_by_test_id("inventory-item-leather-helmet", exact=True)).not_to_be_visible()