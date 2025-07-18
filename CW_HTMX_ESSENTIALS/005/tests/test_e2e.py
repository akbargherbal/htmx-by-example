# Principal Frontend Engineer's Notes:
# This file contains the end-to-end (E2E) tests for our LEGO builder application.
# The purpose of these tests is to simulate a real user's interaction with the
# browser and verify that the HTMX-powered UI behaves exactly as expected.
#
# My testing strategy here is as follows:
#
# 1.  **Single, Comprehensive Scenario:** Instead of many small, isolated tests,
#     I've created one test function that walks through all the user actions in a
#     logical sequence. This mirrors a user's cumulative building process and
#     efficiently validates the final state of the entire system.
#
# 2.  **Strict Adherence to Testing Guide:**
#     - Selectors: All elements are located using their `data-testid` attributes.
#       This is non-negotiable for creating tests that are resilient to style or
#       layout changes.
#     - Assertions: I exclusively use Playwright's `expect()` function. Its built-in
#       auto-waiting mechanism is essential for testing asynchronous applications
#       like ours, as it waits for the DOM to update after an HTMX swap before
#       making an assertion. This eliminates the need for fragile `time.sleep()` calls.
#
# 3.  **Verify Against Backend Truth:** The assertions are written to check for the
#     *exact* content and structure that the backend (`app/main.py`) is known to return.
#     For example, I assert that the new wall contains "Window Wall" and that the
#     drawbridge contains "... a wooden drawbridge ...". This ensures we are testing
#     the true integration between the frontend and backend.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically injected by `conftest.py`.
# The `page` fixture is automatically injected by `pytest-playwright`.

def test_all_buttons_cumulatively_build_final_scene(page: Page, live_server):
    """
    Tests the full user journey of clicking each builder button in sequence
    and verifies that the LEGO scene updates correctly at each step.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Before any action, verify the scene is as expected.
    #    This ensures we're starting from a known, correct state.
    expect(page.get_by_test_id("car-cockpit")).to_contain_text("Empty")
    expect(page.get_by_test_id("wall-section-1-initial")).to_contain_text("Solid Wall")
    # The tree and drawbridge should not exist on the page yet.
    expect(page.get_by_test_id("tree")).not_to_be_visible()
    expect(page.locator("#drawbridge-piece")).not_to_be_visible()

    # 3. Act & Assert: Replace Pilot (innerHTML swap)
    page.get_by_test_id("replace-pilot-button").click()
    # The `expect` function automatically waits for the HTMX swap to complete.
    expect(page.get_by_test_id("car-cockpit")).to_contain_text("LEGO Pilot")
    # Verify the old text is gone.
    expect(page.get_by_test_id("car-cockpit")).not_to_contain_text("Empty")

    # 4. Act & Assert: Swap Wall for Window (outerHTML swap)
    page.get_by_test_id("swap-wall-button").click()
    # The original element with `data-testid="wall-section-1-initial"` is now gone.
    expect(page.get_by_test_id("wall-section-1-initial")).not_to_be_visible()
    # A new element, defined by the backend fragment, now exists.
    final_wall = page.get_by_test_id("wall-section-1-final")
    expect(final_wall).to_be_visible()
    expect(final_wall).to_contain_text("Window Wall")

    # 5. Act & Assert: Add Brick on Top (beforeend swap)
    page.get_by_test_id("add-brick-button").click()
    # The brick is added inside the `#house-walls` container. We verify its presence.
    # The backend fragment for the brick is known to contain the text "Brick".
    expect(page.get_by_test_id("house-walls")).to_contain_text("Brick")

    # 6. Act & Assert: Place Tree Beside House (afterend swap)
    page.get_by_test_id("place-tree-button").click()
    # The tree, with its own test-id from the backend fragment, should now be visible.
    expect(page.get_by_test_id("tree")).to_be_visible()

    # 7. Act & Assert: Get Drawbridge Piece (hx-select and beforebegin swap)
    page.get_by_test_id("get-drawbridge-button").click()
    # The `hx-select` extracts the div with `id="drawbridge-piece"` from the full
    # HTML response. We can now locate this element and verify its content.
    drawbridge = page.locator("#drawbridge-piece")
    expect(drawbridge).to_be_visible()
    # We assert against the specific text content from the backend's HTML fragment.
    expect(drawbridge).to_contain_text("... a wooden drawbridge ...")