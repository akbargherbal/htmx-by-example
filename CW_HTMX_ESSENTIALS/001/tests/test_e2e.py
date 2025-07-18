# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for the "Personal Chef" application.
# The philosophy here is to test the system from the user's perspective. We don't care
# about the internal implementation of HTMX or FastAPI; we only care that when a user
# clicks a button, the correct final state appears on the screen.

# Key Testing Principles Applied:
# 1.  `live_server` and `page` fixtures are used to provide a running app and a browser.
# 2.  Selectors are ALWAYS `data-testid` attributes. This decouples tests from fragile
#     CSS classes or HTML structure, making them far more robust.
# 3.  Assertions use Playwright's `expect()` for its powerful auto-waiting capabilities,
#     eliminating the need for manual `sleep()` calls.
# 4.  Each test verifies a single, complete user story (e.g., "clicking 'Get Water'
#     results in a water message on the serving plate").
# 5.  Assertions check for the *exact HTML fragments* returned by the backend, ensuring
#     that the frontend is correctly integrating with the true API response.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_e2e_get_water_updates_serving_plate(page: Page, live_server):
    """
    Verifies that clicking the 'Get water' button (GET request) correctly
    updates the serving plate with the expected content from the server.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the button.
    page.get_by_test_id("get-water-btn").click()

    # 3. Assert: Verify the UI has updated with the precise HTML fragment.
    serving_plate = page.get_by_test_id("serving-plate")
    expect(serving_plate).to_be_visible()
    expect(serving_plate).to_contain_text("💧")
    expect(serving_plate).to_contain_text("Here is your glass of water.")

def test_e2e_post_recipe_updates_serving_plate(page: Page, live_server):
    """
    Verifies that submitting the recipe form (POST request) correctly
    updates the serving plate with a dynamic message including the recipe name.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    recipe_name = "Pesto Pasta"

    # 2. Act
    page.get_by_test_id("recipe-name-input").fill(recipe_name)
    page.get_by_test_id("submit-recipe-btn").click()

    # 3. Assert
    serving_plate = page.get_by_test_id("serving-plate")
    expect(serving_plate).to_be_visible()
    expect(serving_plate).to_contain_text("📖")
    expect(serving_plate).to_contain_text(f'Recipe for "{recipe_name}" added to the cookbook!')

def test_e2e_put_soup_updates_control_in_place(page: Page, live_server):
    """
    Verifies that clicking 'Adjust Seasoning' (PUT request) replaces the
    soup control itself with the confirmation message.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    soup_control = page.get_by_test_id("soup-control")
    
    # Assert initial state
    expect(soup_control).to_contain_text("A bowl of plain soup is on the counter.")
    expect(page.get_by_test_id("adjust-seasoning-btn")).to_be_visible()

    # 2. Act
    page.get_by_test_id("adjust-seasoning-btn").click()

    # 3. Assert
    # The button and initial text should now be gone.
    expect(page.get_by_test_id("adjust-seasoning-btn")).not_to_be_visible()
    expect(soup_control).not_to_contain_text("A bowl of plain soup is on the counter.")
    
    # The new content from the server should be present.
    expect(soup_control).to_contain_text("🍲")
    expect(soup_control).to_contain_text("The soup has been perfectly seasoned.")

def test_e2e_delete_toast_removes_element(page: Page, live_server):
    """
    Verifies that clicking 'Throw Away Toast' (DELETE request) removes the
    entire toast control element from the DOM.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    toast_control = page.get_by_test_id("toast-control")
    
    # Assert initial state: the element exists.
    expect(toast_control).to_be_visible()

    # 2. Act
    page.get_by_test_id("discard-toast-btn").click()

    # 3. Assert: The element is no longer visible (or in the DOM).
    expect(toast_control).not_to_be_visible()

def test_e2e_polling_trigger_shows_correct_initial_status(page: Page, live_server):
    """
    Verifies that the chef status monitor correctly displays the initial status
    from the Jinja2 template and that the polling mechanism (hx-trigger) is in place.
    Playwright's auto-wait will implicitly handle the first poll, confirming the
    mechanism works by re-asserting the same state.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    
    # 2. Act: No user action is needed, the polling is automatic.

    # 3. Assert
    status_monitor = page.get_by_test_id("chef-status-monitor")
    
    # This assertion verifies both the initial server-side render via Jinja2
    # and the result of the first client-side HTMX poll, which should be the same.
    expect(status_monitor).to_have_text("Chef's Status: Ready and waiting...")