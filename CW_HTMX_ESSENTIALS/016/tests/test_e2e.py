# Principal Engineer Note:
# This E2E test suite uses Playwright to validate the complete user journey.
# The tests are written from the user's perspective, interacting with the browser
# and asserting that the UI updates as expected after HTMX requests.
# Adherence to the `data-testid` convention is non-negotiable for creating
# robust tests that are decoupled from fragile CSS selectors or text content.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_initial_page_load_shows_tshirts(page: Page, live_server):
    """
    Verifies that the initial page loads correctly, rendering the T-shirt
    products by default, as dictated by the backend's `read_root` endpoint.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Verify the initial state is correct.
    # We locate the product content area and check for the T-shirt data that
    # the backend is known to provide on initial load.
    product_area = page.get_by_test_id("product-content-area")
    expect(product_area).to_be_visible()
    expect(product_area).to_contain_text("HTMX Logo Tee")
    expect(product_area).to_contain_text("$28.00")
    expect(product_area).to_contain_text('"I Use Arch" Tee')
    # We also assert that the other category is NOT visible.
    expect(product_area).not_to_contain_text("Classic Snapback")


def test_clicking_hats_link_updates_product_list(page: Page, live_server):
    """
    Tests the `hx-boost` functionality. Verifies that clicking the 'Hats'
    navigation link triggers an HTMX request and correctly swaps the
    product content area with the hats HTML fragment from the server.
    """
    # 1. Arrange: Navigate to the main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the 'Hats' link.
    page.get_by_test_id("nav-hats-link").click()

    # 3. Assert: Verify the UI has updated with the new content.
    # Playwright's `expect` automatically waits for the content to appear.
    product_area = page.get_by_test_id("product-content-area")
    expect(product_area).to_contain_text("Classic Snapback")
    expect(product_area).to_contain_text("$25.00")
    expect(product_area).to_contain_text("Winter Beanie")
    # We also assert that the old content is gone.
    expect(product_area).not_to_contain_text("HTMX Logo Tee")


def test_clicking_place_order_shows_success_message(page: Page, live_server):
    """
    Tests the checkout form. Verifies that clicking 'Place Order' sends a POST
    request and displays the success message from the server in the correct area.
    It also confirms the loading indicator behaves as expected.
    """
    # 1. Arrange: Navigate to the main page.
    page.goto("http://127.0.0.1:8000")

    # Locate the key elements for the test.
    order_button = page.get_by_test_id("place-order-button")
    status_area = page.get_by_test_id("checkout-status-area")
    indicator = page.get_by_test_id("processing-indicator")

    # Assert initial state: status is empty, indicator is hidden.
    expect(status_area).to_be_empty()
    expect(indicator).not_to_be_visible()

    # 2. Act: Simulate the user clicking the 'Place Order' button.
    order_button.click()

    # 3. Assert: Verify the final UI state after the HTMX request.
    # `expect` will wait for the request to complete and the DOM to update.
    # We check that the status area now contains the exact success message from the backend.
    expect(status_area).to_contain_text("✓ Order placed successfully!")

    # We also verify that the loading indicator is hidden again after the request is complete.
    expect(indicator).not_to_be_visible()