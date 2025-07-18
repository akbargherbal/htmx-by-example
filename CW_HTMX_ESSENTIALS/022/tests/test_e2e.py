# Principal Frontend Engineer's Notes:
#
# This E2E test suite uses Playwright to verify the complete user workflow. My philosophy
# for E2E tests is to simulate a user's journey as closely as possible and assert on the
# final, visible outcomes. This test validates the entire system: the browser, HTMX,
# and the FastAPI backend, all working together.
#
# Key Testing Strategies:
# 1.  Test the Full Flow: Instead of many small tests, one comprehensive test function,
#     `test_full_garden_crud_and_polling_workflow`, covers the entire "happy path"
#     (Create, Replace, Delete, and Polling). This mirrors how a user would interact
#     with the page and provides high value by testing the integration of all features.
#
# 2.  `data-testid` Selectors: All element selections use `page.get_by_test_id()`. This is
#     the most robust strategy, as it decouples tests from fragile selectors like CSS
#     classes or text content, which are likely to change.
#
# 3.  Playwright's `expect` and Auto-Waiting: I exclusively use `expect()` for assertions.
#     Its built-in auto-waiting mechanism is essential for testing dynamic applications.
#     For example, when we check for the "Garden is Thriving" status, `expect()` will
#     automatically wait for the polling request to complete and the DOM to update. This
#     eliminates the need for unreliable `time.sleep()` calls.
#
# 4.  Asserting on Backend Truth: The assertions check for the *exact* HTML fragments
#     and states that the backend (`app/main.py`) is known to produce. For instance, we
#     assert that the "Tomato" plot is replaced by a "Carrot" plot, which is the specific
#     logic implemented in the `replace_plant` endpoint. This ensures our frontend and
#     backend are perfectly in sync.

from playwright.sync_api import Page, expect
import re

# The `live_server` fixture is automatically injected by pytest from conftest.py.
# The `page` fixture is automatically injected by pytest-playwright.

def test_full_garden_crud_and_polling_workflow(page: Page, live_server):
    """
    Verifies the entire user journey:
    1. Loads the page and sees the initial state (Tomato, Weed).
    2. Verifies the initial polled status shows "Needs Weeding".
    3. Deletes the weed and sees the plot disappear.
    4. Verifies the polled status updates to "Garden is Thriving".
    5. Creates a new "Basil" plant and sees it appear.
    6. Replaces the "Tomato" plant and sees it become a "Carrot".
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Check that the initial plots and status are correct.
    #    The page should load with a Tomato and a Weed.
    initial_tomato_plot = page.get_by_test_id("plant-plot-tomato")
    initial_weed_plot = page.get_by_test_id("plant-plot-weed")
    expect(initial_tomato_plot).to_be_visible()
    expect(initial_tomato_plot).to_contain_text("🍅 Tomato")
    expect(initial_weed_plot).to_be_visible()
    expect(initial_weed_plot).to_contain_text("🌿 Weed")

    # The status polls on load. Because a weed exists, it should show "Needs Weeding".
    # Playwright's `expect` will wait for the initial "Loading..." text to be replaced.
    status_display = page.get_by_test_id("garden-status-after")
    expect(status_display).to_contain_text("🚨 Needs Weeding")

    # 3. Act & Assert (DELETE): Pull the weed.
    # We must handle the confirmation dialog that we configured with `hx-confirm`.
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_test_id("pull-weed-button-2").click()

    # The weed plot should now be gone.
    expect(initial_weed_plot).not_to_be_visible()

    # 4. Assert (Polling Update): The status should update automatically.
    # `expect` will wait for the next poll (within 3s) to complete and update the text.
    expect(status_display).to_contain_text("✨ Garden is Thriving")

    # 5. Act & Assert (CREATE): Plant a new seed.
    plant_name_input = page.get_by_test_id("plant-name-input")
    plant_name_input.fill("Basil")
    page.get_by_test_id("plant-seed-button").click()

    # A new plot for Basil should appear.
    new_basil_plot = page.get_by_test_id("plant-plot-basil")
    expect(new_basil_plot).to_be_visible()
    expect(new_basil_plot).to_contain_text("🌱 Basil")
    # Also assert that the input field was cleared after submission.
    expect(plant_name_input).to_be_empty()

    # 6. Act & Assert (UPDATE): Replace the Tomato plant.
    page.get_by_test_id("replace-plant-button-1").click()

    # The original tomato plot should be gone.
    expect(initial_tomato_plot).not_to_be_visible()
    # A new carrot plot should have replaced it, reusing the same plot ID.
    replaced_carrot_plot = page.get_by_test_id("plant-plot-carrot")
    expect(replaced_carrot_plot).to_be_visible()
    expect(replaced_carrot_plot).to_contain_text("🥕 Carrot")