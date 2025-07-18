# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for our restaurant application.
# We use Playwright to simulate a real user interacting with the browser.
# The goal is to verify that user actions (clicks, form submissions) trigger the correct
# HTMX requests and that the UI updates with the exact HTML fragments returned by the backend.
# This ensures the entire system (frontend HTML -> HTMX -> backend API) works together correctly.

from playwright.sync_api import Page, expect
import re # Import the regular expression module for class assertions

# The `live_server` fixture is automatically provided by conftest.py.
# The `page` fixture is automatically provided by pytest-playwright.

def test_initial_page_load_shows_empty_plate(page: Page, live_server):
    """
    Verifies that when a user first visits the page, the "Your Table" section
    correctly displays the initial "empty plate" message.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Verify the initial UI state.
    # We locate the target area by its data-testid for a stable selector.
    plate_area = page.get_by_test_id("plate-display-area")

    # We expect the initial message to be visible within this area.
    expect(plate_area).to_be_visible()
    expect(plate_area).to_contain_text("Your plate is empty. Place an order from the menu.")

def test_clicking_order_soup_updates_plate(page: Page, live_server):
    """
    Verifies that clicking the 'Order Soup' button triggers an HTMX GET request
    and correctly swaps the response content into the plate area.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the soup button.
    page.get_by_test_id("order-soup-button").click()

    # 3. Assert: Verify the UI has updated with the soup HTML fragment.
    plate_area = page.get_by_test_id("plate-display-area")

    # Assert that the correct content is now visible.
    expect(plate_area).to_contain_text("Soup of the Day")
    expect(plate_area).to_contain_text("Enjoy your hot and delicious soup!")

    # Crucially, we also verify structural and styling details from the backend's
    # HTML fragment to ensure the integration is perfect. Here we check for the
    # specific background color class the backend sends for the soup order.
    # Using a regex is a robust way to check for a class among potentially many.
    expect(plate_area.locator("div").first).to_have_class(re.compile(r"bg-yellow-900/30"))

def test_clicking_order_special_updates_plate(page: Page, live_server):
    """
    Verifies that clicking the 'Order Daily Special' button triggers an HTMX GET request
    and correctly swaps the response content into the plate area.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the special button.
    page.get_by_test_id("order-special-button").click()

    # 3. Assert: Verify the UI has updated with the special's HTML fragment.
    plate_area = page.get_by_test_id("plate-display-area")

    # Assert that the correct content is now visible.
    expect(plate_area).to_contain_text("Daily Special")
    expect(plate_area).to_contain_text("Perfectly grilled salmon with a side of asparagus.")

    # Verify the specific background color class for the special order.
    expect(plate_area.locator("div").first).to_have_class(re.compile(r"bg-cyan-900/30"))

def test_submitting_custom_burger_form_updates_plate(page: Page, live_server):
    """
    Verifies that filling out and submitting the 'Build-a-Burger' form triggers
    an HTMX POST request and displays the customized order confirmation.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user filling out the form and submitting it.
    page.get_by_test_id("topping-lettuce").check()
    page.get_by_test_id("topping-cheese").check()
    page.get_by_test_id("special-requests-input").fill("extra pickles, toasted bun")
    page.get_by_test_id("place-custom-order-button").click()

    # 3. Assert: Verify the UI has updated with the custom burger confirmation.
    plate_area = page.get_by_test_id("plate-display-area")

    # Assert that the confirmation title and dynamic content are present.
    expect(plate_area).to_contain_text("Your Custom Burger is Ready!")
    # Check for the specific toppings that were selected.
    expect(plate_area.locator("li:has-text('Lettuce')")).to_be_visible()
    expect(plate_area.locator("li:has-text('Cheese')")).to_be_visible()
    # Check that the special request text was included.
    expect(plate_area).to_contain_text("extra pickles, toasted bun")

    # Verify the specific background color class for the custom order.
    expect(plate_area.locator("div").first).to_have_class(re.compile(r"bg-green-900/30"))