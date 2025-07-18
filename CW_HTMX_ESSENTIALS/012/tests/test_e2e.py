# Principal Frontend Engineer Notes:
#
# This E2E test suite uses Playwright to verify the complete system, from user
# interaction in the browser to the final UI state rendered by the backend.
#
# Key Testing Principles Applied:
# 1.  User-Centric Scenarios: Each test function simulates a distinct user journey
#     (e.g., successful submission, handling a 404 error).
# 2.  `data-testid` Selectors: We exclusively use `data-testid` attributes for
#     locating elements. This decouples our tests from fragile selectors like
#     CSS classes or element structure, making them far more resilient to
#     styling changes.
# 3.  `expect()` with Auto-Waiting: Playwright's `expect()` function is used for
#     all assertions. It has built-in auto-waiting, which intelligently waits for
#     the UI to reach the expected state after an HTMX request. This eliminates
#     the need for unreliable `time.sleep()` calls.
# 4.  Asserting on Backend Truth: The assertions check for the *exact* HTML content
#     and structure that we know the backend returns. This ensures we are testing
#     the true integration, not just a superficial text match.

from playwright.sync_api import Page, expect

# The `live_server` fixture (from conftest.py) and `page` fixture (from pytest-playwright)
# are automatically injected by pytest.

def test_initial_page_load_displays_correct_state(page: Page, live_server):
    """
    Verifies that the page loads with the correct initial content before any user interaction.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Check the initial state of key components.
    # The status display should show the default "awaiting" message.
    initial_status = page.get_by_test_id("mail_status_display")
    expect(initial_status).to_be_visible()
    expect(initial_status).to_contain_text("Awaiting transmission...")

    # The customer ID should be displayed correctly.
    customer_id_display = page.get_by_test_id("customer_id_display")
    expect(customer_id_display).to_contain_text("CID-12345")


def test_successful_address_change_updates_status(page: Page, live_server):
    """
    Tests the "happy path": filling the form, clicking submit, and verifying the success message.
    """
    # 1. Arrange: Navigate to the page and fill out the form.
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("street_address_input").fill("456 Oak Ave")
    page.get_by_test_id("zip_code_input").fill("10001")

    # 2. Act: Simulate the user clicking the submit button.
    page.get_by_test_id("submit_button").click()

    # 3. Assert: Verify the UI has updated with the precise success HTML from the backend.
    status_display = page.get_by_test_id("mail_status_display")
    
    # Check for the key text content.
    expect(status_display).to_contain_text("Success!")
    # This assertion confirms that hx-include and hx-vals worked correctly.
    expect(status_display).to_contain_text("Request processed for customer CID-12345 (Service: Express).")
    expect(status_display).to_contain_text("Address successfully updated to 456 Oak Ave, 10001.")

    # A more robust check to ensure the correct styling/container was returned.
    success_div = status_display.locator("div")
    expect(success_div).to_have_class("p-4 bg-green-900/50 border border-green-700 rounded-md text-green-300")


def test_invalid_zip_submission_shows_404_error(page: Page, live_server):
    """
    Tests that clicking the 'Send to Invalid Zip Code' button correctly displays the 404 error message.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button designed to trigger a 404 error.
    page.get_by_test_id("error_button_404").click()

    # 3. Assert: Verify the UI shows the specific 404 error fragment from the backend.
    status_display = page.get_by_test_id("mail_status_display")
    expect(status_display).to_contain_text("Error: Not Found (404)")
    expect(status_display).to_contain_text("The destination zip code could not be found. Please check the address and try again.")

    # Verify the error styling.
    error_div = status_display.locator("div")
    expect(error_div).to_have_class("p-4 bg-red-900/50 border border-red-700 rounded-md text-red-300")


def test_server_failure_simulation_shows_500_error(page: Page, live_server):
    """
    Tests that clicking the 'Break the Sorting Machine' button correctly displays the 500 error message.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button designed to trigger a 500 internal server error.
    page.get_by_test_id("error_button_500").click()

    # 3. Assert: Verify the UI shows the specific 500 error fragment from the backend.
    status_display = page.get_by_test_id("mail_status_display")
    expect(status_display).to_contain_text("Error: Internal Server Error (500)")
    expect(status_display).to_contain_text("The mail sorting machine is offline. We are unable to process your request at this time.")

    # Verify the error styling.
    error_div = status_display.locator("div")
    expect(error_div).to_have_class("p-4 bg-yellow-900/50 border border-yellow-700 rounded-md text-yellow-300")