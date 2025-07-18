# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for the vending machine UI.
# E2E tests simulate real user interactions in a browser, providing the highest confidence
# that the integrated system (frontend HTML + HTMX + backend API) works as intended.
# We use Playwright for its robust and reliable browser automation capabilities.
#
# Key Principles Followed:
# 1. Selectors: Strictly use `data-testid` attributes for selectors. This decouples tests
#    from fragile implementation details like CSS classes or element structure.
# 2. Assertions: Use Playwright's `expect()` for all assertions. It has built-in
#    auto-waiting, which makes tests far more reliable by eliminating the need for `time.sleep()`.
# 3. User Journeys: Each test represents a complete user story, from initial state to final outcome.

from playwright.sync_api import Page, expect

# The `live_server` fixture (from conftest.py) and `page` fixture (from pytest-playwright)
# are automatically injected into each test function by pytest.

def test_initial_state_is_correct(page: Page, live_server):
    """
    Verifies that the page loads with the correct initial state as rendered by the backend.
    This includes checking the initial credit and the state of the item buttons.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Verify the initial UI state.
    # Check that the credit display shows $0.00.
    credit_display = page.get_by_test_id("credit_display")
    expect(credit_display).to_have_text("$0.00")

    # Check that the button for an affordable item ($0.50) is disabled due to lack of funds.
    # The backend logic determines this state, and we verify it's rendered correctly.
    unaffordable_button = page.get_by_test_id("item_selection_button-D4-unaffordable")
    expect(unaffordable_button).to_be_visible()
    expect(unaffordable_button).to_be_disabled()

    # Check that the button for a sold-out item correctly displays "SOLD OUT".
    sold_out_button = page.get_by_test_id("item_selection_button-B2-sold-out")
    expect(sold_out_button).to_be_visible()
    expect(sold_out_button).to_have_text("SOLD OUT")
    expect(sold_out_button).to_be_disabled()

def test_get_item_info_updates_display(page: Page, live_server):
    """
    Tests the hx-get interaction: clicking an item's info area should update the display screen.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    display_screen = page.get_by_test_id("display_screen_target")
    item_to_click = page.get_by_test_id("item_info_button-A1")

    # 2. Act: Simulate the user clicking the item info area.
    item_to_click.click()

    # 3. Assert: Verify the display screen now contains the precise HTML fragment
    #    returned by the `/item-info/A1` backend endpoint.
    expect(display_screen).to_contain_text("A1: Crispy Chips")
    expect(display_screen).to_contain_text("Calories: 150, Sodium: 200mg")

def test_add_credit_updates_credit_and_enables_buttons(page: Page, live_server):
    """
    Tests that adding credit updates the credit display (via OOB swap) and re-renders
    the item grid, enabling a previously unaffordable item's purchase button.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    add_credit_button = page.get_by_test_id("add_credit_button")
    credit_display = page.get_by_test_id("credit_display")
    
    # Verify initial state: button for item A1 ($0.75) is disabled.
    expect(page.get_by_test_id("item_selection_button-A1-unaffordable")).to_be_visible()

    # 2. Act: Click the "Add Credit" button three times to reach $0.75.
    add_credit_button.click() # Credit becomes $0.25
    add_credit_button.click() # Credit becomes $0.50
    add_credit_button.click() # Credit becomes $0.75

    # 3. Assert
    # The credit display should be updated by the OOB swap.
    expect(credit_display).to_have_text("$0.75")
    
    # The item grid should have been re-rendered. The button for item A1 should now
    # be enabled, and its test-id will have changed accordingly.
    enabled_button = page.get_by_test_id("item_selection_button-A1-enabled")
    expect(enabled_button).to_be_visible()
    expect(enabled_button).to_be_enabled()

def test_successful_purchase_updates_credit_and_retrieval_bin(page: Page, live_server):
    """
    Tests a full, successful purchase journey. This verifies that multiple OOB swaps
    (for credit and the retrieval bin) work correctly from a single user action.
    """
    # 1. Arrange: Add enough credit to purchase item A1 ($0.75).
    page.goto("http://127.0.0.1:8000")
    add_credit_button = page.get_by_test_id("add_credit_button")
    add_credit_button.click()
    add_credit_button.click()
    add_credit_button.click()

    # 2. Act: Click the now-enabled purchase button for item A1.
    purchase_button = page.get_by_test_id("item_selection_button-A1-enabled")
    purchase_button.click()

    # 3. Assert
    # The credit display should be updated to $0.00 ($0.75 - $0.75).
    credit_display = page.get_by_test_id("credit_display")
    expect(credit_display).to_have_text("$0.00")

    # The retrieval bin should now contain the purchased item. We check for the
    # specific HTML fragment that the backend sends.
    retrieval_bin = page.get_by_test_id("retrieval_bin_target")
    expect(retrieval_bin).to_contain_text("Crispy Chips")

def test_purchase_sold_out_item_shows_error_on_screen(page: Page, live_server):
    """
    Tests the global error handling. Since the UI correctly disables the button for
    a sold-out item, we can't click it. Instead, we manually trigger the HTMX request
    using Playwright's `page.evaluate` to confirm that if such a request *were* made,
    our `hx-on::htmx:responseError` handler would correctly display the error.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    display_screen = page.get_by_test_id("display_screen_target")
    
    # Verify the initial state of the display screen.
    expect(display_screen).to_contain_text("Welcome! Select an item for info.")

    # 2. Act: Use page.evaluate to execute JavaScript in the browser context.
    # We manually tell HTMX to issue a POST request to the endpoint for the sold-out item.
    # This simulates the network request that is normally prevented by the UI.
    page.evaluate("htmx.ajax('POST', '/purchase/B2', { swap: 'none' })")

    # 3. Assert: The `htmx:responseError` handler on the `<body>` tag should have
    # caught the 404 response and placed its HTML content into the display screen.
    expect(display_screen).to_contain_text("SOLD OUT")
    expect(display_screen).to_contain_text("Item B2 is unavailable.")