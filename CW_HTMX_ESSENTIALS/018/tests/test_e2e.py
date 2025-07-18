# Principal Engineer's Note:
# This E2E test suite uses Playwright to verify the complete system from the user's perspective.
# Each test simulates a user clicking a button and asserts that the UI updates with the *exact*
# HTML fragment returned by the live backend. This validates that the frontend (HTMX attributes)
# and backend (API responses) are correctly integrated.
# We strictly use `data-testid` for selectors and `expect` for assertions, adhering to best practices.

from playwright.sync_api import Page, expect

# The `live_server` fixture (from conftest.py) and `page` fixture (from pytest-playwright)
# are automatically injected by pytest.

def test_e2e_404_request_updates_inbox_with_error_message(page: Page, live_server):
    """
    Verifies that clicking the 'Request Missing File (404)' button correctly
    triggers an HTMX request and swaps the 404 error HTML from the server into the inbox.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the button that triggers a 404 response.
    page.get_by_test_id("request-404-btn").click()

    # 3. Assert: Verify the UI has updated with the specific 404 error message.
    # We look for the element by the data-testid that the backend is known to return.
    error_message = page.get_by_test_id("inbox-404-state")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("File Not Found. The requested employee file does not exist.")


def test_e2e_500_request_updates_error_banner_out_of_band(page: Page, live_server):
    """
    Verifies that a 500 server error is handled out-of-band. The inbox content
    should NOT change, but the dedicated error banner should display an alert.
    This tests the global `htmx:responseError` handler.
    """
    # 1. Arrange: Navigate to the app and confirm initial states.
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("inbox-initial-state")).to_be_visible()
    expect(page.get_by_test_id("error-banner-content")).to_be_empty()

    # 2. Act: Simulate clicking the button that triggers a 500 response.
    page.get_by_test_id("request-500-btn").click()

    # 3. Assert:
    # The primary inbox content should remain unchanged.
    expect(page.get_by_test_id("inbox-initial-state")).to_be_visible()

    # The out-of-band error banner should now contain the alert message.
    error_banner = page.get_by_test_id("error-banner-500-state")
    expect(error_banner).to_be_visible()
    expect(error_banner).to_contain_text("A communication error occurred. Please try again later.")


def test_e2e_redirect_request_updates_inbox_with_final_content(page: Page, live_server):
    """
    Verifies that HTMX correctly handles an `HX-Redirect` header. The user clicks
    a button, the backend responds with a redirect, HTMX follows it, and the content
    from the final destination is swapped into the inbox.
    """
    # 1. Arrange: Navigate to the running application.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate clicking the button that triggers the redirect.
    page.get_by_test_id("request-redirect-btn").click()

    # 3. Assert: Verify the UI shows the content from the *redirected* URL.
    # We look for the data-testid returned by the `/mail/new-department` endpoint.
    redirect_message = page.get_by_test_id("inbox-redirect-state")
    expect(redirect_message).to_be_visible()
    expect(redirect_message).to_contain_text("Your request was rerouted and received by the correct department.")