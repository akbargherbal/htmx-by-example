# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) test suite for the Smart Car Dashboard.
# E2E tests are the ultimate proof that the frontend (HTML/HTMX) and backend (FastAPI)
# are correctly integrated. We use Playwright to simulate real user actions in a browser.
#
# Key Testing Principles Applied:
# - User-Centric Scenarios: Each test function represents a complete user journey,
#   from navigating to the page to clicking a button and seeing the result.
# - `data-testid` Selectors: We exclusively use `data-testid` attributes for selecting
#   elements. This makes tests resilient to changes in styling or HTML structure.
# - `expect` Assertions: Playwright's `expect()` function is used for all assertions.
#   It has built-in auto-waiting, which eliminates flaky tests by waiting for the UI
#   to update before checking the result.
# - Asserting on Backend Truth: Assertions check for the *exact* HTML fragments that
#   the backend is known to produce. This verifies the complete system, not just the frontend.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_initial_load_and_polling_updates_fuel_gauge(page: Page, live_server):
    """
    Verifies that the fuel gauge shows the correct initial value on page load
    and that the polling mechanism successfully updates the content.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert (Initial Load): Verify the fuel gauge displays the initial value (98%)
    #    rendered by the server-side Jinja2 template.
    fuel_display = page.get_by_test_id("fuel-gauge-container").locator("#fuel-gauge-display")
    expect(fuel_display).to_have_text("Fuel: 98%")

    # 3. Assert (Polling Update): The `hx-trigger="load"` also fires an immediate request.
    #    We verify that the content is replaced with the HTML fragment from the backend.
    #    Playwright's `expect` will wait for the HTMX swap to complete.
    #    The assertion checks for the specific class from the backend's HTML fragment.
    expect(fuel_display.locator("p.text-green-400")).to_have_text("Fuel: 98%")

def test_calculate_route_without_tolls(page: Page, live_server):
    """
    Tests the navigation form submission without the 'Avoid Tolls' option.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Fill the destination and click the calculate button.
    page.get_by_test_id("destination-input").fill("City Hall")
    page.get_by_test_id("calculate-route-button").click()

    # 3. Assert: Verify the UI updates with the correct message from the backend.
    #    We check for the exact HTML fragment returned by the `/api/calculate-route` endpoint.
    result_display = page.get_by_test_id("route-result-display")
    expect(result_display.locator("p.text-green-400")).to_have_text(
        "Route to 'City Hall' via the fastest route is being calculated..."
    )

def test_calculate_route_with_tolls(page: Page, live_server):
    """
    Tests the navigation form submission with the 'Avoid Tolls' option checked.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act
    page.get_by_test_id("destination-input").fill("The Airport")
    page.get_by_test_id("avoid-tolls-checkbox").check()
    page.get_by_test_id("calculate-route-button").click()

    # 3. Assert: Verify the UI updates with the "avoiding tolls" message.
    result_display = page.get_by_test_id("route-result-display")
    expect(result_display.locator("p.text-green-400")).to_have_text(
        "Route to 'The Airport' avoiding tolls is being calculated..."
    )

def test_404_error_is_handled_and_displayed_in_alert_panel(page: Page, live_server):
    """
    Verifies that a 404 Not Found error from the backend is caught by the global
    JavaScript error handler and displayed correctly in the alert panel.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button that is known to trigger a 404 error.
    page.get_by_test_id("tune-invalid-station-button").click()

    # 3. Assert: Verify the alert panel is populated with the correct error message.
    alert_panel = page.get_by_test_id("alert-panel")
    expect(alert_panel).to_be_visible()
    expect(alert_panel).to_contain_text("Error: The requested feature could not be found.")
    # Also verify the class change, which indicates the error styling was applied.
    expect(alert_panel).to_have_class(
        "min-h-[60px] bg-red-900/50 border border-red-700 text-red-300 rounded-md p-4 flex items-center"
    )

def test_500_error_is_handled_and_displayed_in_alert_panel(page: Page, live_server):
    """
    Verifies that a 500 Internal Server Error is caught and displayed.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button that triggers a 500 error.
    page.get_by_test_id("check-broken-sensor-button").click()

    # 3. Assert: Verify the alert panel shows the server error message.
    alert_panel = page.get_by_test_id("alert-panel")
    expect(alert_panel).to_be_visible()
    expect(alert_panel).to_contain_text("Error: A critical server error occurred. Please try again later.")

def test_redirect_header_navigates_to_new_page(page: Page, live_server):
    """
    Verifies that a response with an HX-Redirect header correctly navigates
    the browser to the specified URL.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button that triggers the redirect.
    page.get_by_test_id("access-race-mode-button").click()

    # 3. Assert: Playwright automatically follows the redirect. We verify that
    #    the browser has navigated to the new page and that the content is correct.
    expect(page).to_have_url("http://127.0.0.1:8000/page/driving-mode-selection")
    expect(page.locator("h1")).to_have_text("Driving Mode Selection")
    expect(page).to_have_title("Mode Selection")