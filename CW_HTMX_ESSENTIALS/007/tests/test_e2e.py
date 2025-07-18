# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for the Drive-Thru application.
# E2E tests are the ultimate proof that the frontend (HTMX) and backend (FastAPI)
# are correctly integrated. We use Playwright to simulate real user actions.
#
# Key Principles Followed:
# 1. Use `data-testid` for selectors: This makes tests resilient to style or layout changes.
# 2. Assert on final UI state: We verify what the user actually sees in the browser.
# 3. Test complete user journeys: Each test represents a realistic user interaction from start to finish.
# 4. Rely on Playwright's auto-waiting: `expect()` automatically waits for the UI to update,
#    eliminating the need for fragile `time.sleep()` calls.

from playwright.sync_api import Page, expect

# The `live_server` and `reset_state_before_each_e2e_test` fixtures are automatically
# provided by conftest.py. The `page` fixture is from pytest-playwright.

def test_initial_page_load_shows_empty_order(page: Page, live_server):
    """
    Verifies that the application loads correctly and the initial state
    of the order summary is empty, as rendered by the server.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Check that the order summary initially shows the "empty" message.
    # This confirms that the Jinja2 template on the backend is correctly rendering the initial state.
    order_summary = page.get_by_test_id("order-summary")
    expect(order_summary).to_be_visible()
    expect(order_summary).to_contain_text("Your order is empty.")

def test_add_first_item_updates_order_summary(page: Page, live_server):
    """
    Tests the primary user journey: adding a single item to an empty order.
    Verifies that the HTMX POST request succeeds and updates the summary panel.
    """
    # 1. Arrange: Navigate to the app.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user selecting an item, setting a quantity, and submitting the form.
    page.get_by_test_id("item-select").select_option("Cheeseburger")
    page.get_by_test_id("quantity-input").fill("2")
    page.get_by_test_id("submit-button").click()

    # 3. Assert: Verify the UI has updated with the precise HTML fragment
    #    that the backend service is known to return. Playwright's `expect` will
    #    automatically wait for the HTMX swap to complete.
    order_summary = page.get_by_test_id("order-summary")
    expect(order_summary).to_contain_text("2 x Cheeseburger")
    # Also assert that the initial empty message is gone.
    expect(order_summary).not_to_contain_text("Your order is empty.")

def test_add_two_different_items_shows_both_in_summary(page: Page, live_server):
    """
    Tests that adding two different items results in both being displayed in the order summary.
    This verifies that the backend is correctly managing the list of items.
    """
    # 1. Arrange: Navigate to the app.
    page.goto("http://127.0.0.1:8000")

    # 2. Act (First Item): Add French Fries.
    page.get_by_test_id("item-select").select_option("French Fries")
    page.get_by_test_id("quantity-input").fill("1")
    page.get_by_test_id("submit-button").click()

    # 3. Assert (First Item): Wait for the first update to complete.
    order_summary = page.get_by_test_id("order-summary")
    expect(order_summary).to_contain_text("1 x French Fries")

    # 4. Act (Second Item): Add a Milkshake.
    page.get_by_test_id("item-select").select_option("Milkshake")
    page.get_by_test_id("quantity-input").fill("1")
    page.get_by_test_id("submit-button").click()

    # 5. Assert (Final State): Verify that the summary now contains both items.
    # This confirms the backend returned a fragment with the complete, updated list.
    expect(order_summary).to_contain_text("1 x French Fries")
    expect(order_summary).to_contain_text("1 x Milkshake")

def test_add_existing_item_updates_quantity_in_summary(page: Page, live_server):
    """
    Tests that adding an item that is already in the order correctly updates
    the quantity instead of adding a new line item.
    """
    # 1. Arrange: Navigate and add an initial item.
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("item-select").select_option("Soda")
    page.get_by_test_id("quantity-input").fill("1")
    page.get_by_test_id("submit-button").click()

    # 2. Assert (Initial State): Wait for the first update.
    order_summary = page.get_by_test_id("order-summary")
    expect(order_summary).to_contain_text("1 x Soda")

    # 3. Act: Add the *same* item again with an additional quantity.
    page.get_by_test_id("item-select").select_option("Soda")
    page.get_by_test_id("quantity-input").fill("2")
    page.get_by_test_id("submit-button").click()

    # 4. Assert (Final State): Verify the quantity is updated to the sum (1 + 2 = 3).
    # This is a critical test for the backend logic, confirmed via the UI.
    expect(order_summary).to_contain_text("3 x Soda")
    # Also, ensure the old line item is gone, not just appended to.
    expect(order_summary).not_to_contain_text("1 x Soda")