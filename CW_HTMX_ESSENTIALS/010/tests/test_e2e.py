# Principal Engineer's Note on E2E Testing Strategy:
# This file contains the end-to-end tests for our Airport Terminal UI.
# Our philosophy is to test the system from the user's perspective, verifying
# that their actions lead to the correct, visible outcomes on the page.
#
# Key Principles Followed:
# 1.  User-Centric Scenarios: Each test function simulates a complete user journey,
#     like clicking a flight to see details or scanning a pass to get redirected.
# 2.  `data-testid` Selectors: We exclusively use `data-testid` attributes for selecting
#     elements. This decouples our tests from fragile CSS classes or HTML structure,
#     making them far more robust against UI refactoring.
# 3.  `expect` for Assertions: We use Playwright's `expect()` function, which has
#     built-in auto-waiting. This eliminates flaky tests caused by race conditions,
#     as Playwright will wait for the UI to settle before making an assertion.
# 4.  Verifying True Integration: Assertions check for the *exact* content and structure
#     that the backend is known to return. This proves that the frontend (HTMX attributes)
#     and backend (HTML fragment generation) are correctly wired together.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_initial_load_and_flight_details_boost(page: Page, live_server):
    """
    Verifies that the page loads with the correct initial flight data and that
    clicking a flight link (hx-boost) correctly updates the details panel
    without a full page reload.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Verify the initial state is rendered correctly.
    # The backend's `read_root` serves the "updated" state on first load.
    initial_board = page.get_by_test_id("departures-board-content")
    expect(initial_board.get_by_text("FL123")).to_be_visible()
    expect(initial_board.get_by_text("A2 (Gate Change)")).to_be_visible()
    expect(initial_board.get_by_text("Boarding")).to_be_visible()

    details_panel = page.get_by_test_id("flight-details-panel")
    expect(details_panel).to_contain_text("Click a flight on the departures board to see details here.")

    # 3. Act: Simulate a user clicking the link for flight FL123.
    # We target the `<a>` tag within the test-id'd cell for a precise click.
    page.get_by_test_id("flight-row-link-FL123-updated").get_by_role("link", name="FL123").click()

    # 4. Assert Final State: Verify the details panel was updated with the
    #    exact content returned by the `/flights/FL123` endpoint.
    expect(details_panel).to_contain_text("Flight FL123 Details")
    expect(details_panel).to_contain_text("Airline: American Airlines")
    expect(details_panel).to_contain_text("Aircraft: Boeing 777")
    expect(details_panel).to_contain_text("Status: Boarding")
    expect(details_panel).to_contain_text("Gate: A2 (Gate Change)")
    # Crucially, assert the URL did *not* change, proving it was an HTMX swap, not a navigation.
    expect(page).to_have_url("http://127.0.0.1:8000/")


def test_urgent_update_refreshes_departures_board(page: Page, live_server):
    """
    Verifies that clicking the 'Trigger Urgent Gate Change' button sends a POST
    request and that the subsequent `HX-Trigger` header correctly causes the
    departures board to fire a GET request to refresh itself.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act & Assert: This is a more advanced test. We want to prove that clicking
    # the button *causes* a network request to `/api/flights`. We use Playwright's
    # network request interception to wait for this specific event.
    # This is the most reliable way to test an `HX-Trigger` mechanism.
    with page.expect_request("**/api/flights") as request_info:
        page.get_by_test_id("urgent-update-button").click()

    # The `with` block will automatically wait for the request to happen.
    # If it times out, the test fails.
    request = request_info.value
    expect(request.method).to_equal("GET")
    # We can also check the response to be sure it completed successfully.
    response = request.response()
    expect(response.status).to_equal(200)


def test_scan_standard_pass_triggers_redirect(page: Page, live_server):
    """
    Verifies that submitting the form with 'Standard' ticket type triggers a
    server-side redirect via the `HX-Redirect` header, causing the browser
    to navigate to the /access-denied page.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Select 'Standard' and click the scan button.
    page.get_by_test_id("ticket-type-select").select_option("Standard")
    page.get_by_test_id("scan-pass-button").click()

    # 3. Assert: Verify the browser has navigated to the new page.
    # `expect(page).to_have_url()` has auto-waiting, so it will wait for the redirect to complete.
    expect(page).to_have_url("http://127.0.0.1:8000/access-denied")
    # Verify the content of the new page is correct.
    expect(page.get_by_role("heading", name="ACCESS DENIED")).to_be_visible()
    expect(page.get_by_text("Standard tickets do not grant access to this area.")).to_be_visible()


def test_departures_board_is_configured_for_polling(page: Page, live_server):
    """
    Verifies that the departures board `<tbody>` element has the correct `hx-trigger`
    attribute to enable polling. This is a static check of the configuration,
    which is more reliable and faster than trying to wait for a poll to occur.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Locate the element responsible for polling.
    departures_board = page.get_by_test_id("departures-board-content")

    # 3. Assert: Check that the `hx-trigger` attribute has the exact value
    # required for both polling and urgent updates.
    expect(departures_board).to_have_attribute("hx-trigger", "every 30s, urgentUpdate from:body")