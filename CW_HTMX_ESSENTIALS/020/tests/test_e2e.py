# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for the Chemistry Lab application.
# E2E tests are critical because they verify the entire system from the user's
# perspective, ensuring that the HTMX-powered frontend correctly communicates with
# the FastAPI backend and that the UI updates as expected.
#
# Key Testing Strategies:
# 1.  **User-Centric Scenarios:** Each test function simulates a specific user journey,
#     like "mixing a safe combination" or "starting a failing experiment."
# 2.  **`data-testid` Selectors:** We exclusively use `data-testid` attributes for selecting
#     elements. This decouples tests from fragile selectors like CSS classes or text content,
#     making them more resilient to cosmetic UI changes.
# 3.  **`expect` Assertions:** Playwright's `expect()` function is used for all assertions.
#     It has built-in auto-waiting, which eliminates the need for manual `sleep()` calls
#     and makes tests more reliable by waiting for the UI to reach the expected state.
# 4.  **Network Interception:** For the polling test, `page.route()` is used to intercept
#     the `/temperature` network request and provide a mock response. This allows us to
#     test the polling behavior reliably and quickly, without having to wait for the
#     actual 5-second interval or manipulate backend state.

from playwright.sync_api import Page, expect
import re

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_e2e_successful_mix_updates_log(page: Page, live_server):
    """
    Verifies that submitting the 'Mix Chemicals' form with a safe combination
    updates the success log and does NOT trigger the emergency alert.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Select a safe combination of chemicals and submit the form.
    page.get_by_label("Chemical A").select_option("Alkaline Solution")
    page.get_by_label("Chemical B").select_option("Inert Base")
    page.get_by_test_id("mix_chemicals_form").get_by_role("button").click()

    # 3. Assert: Verify the UI has updated correctly.
    # The success log should contain the exact text returned by the backend.
    success_log = page.get_by_test_id("reaction_result")
    expect(success_log).to_contain_text("[SUCCESS LOG] Mix complete: Alkaline Solution + Inert Base formed.")
    
    # The emergency alert should remain hidden.
    emergency_alert = page.get_by_test_id("emergency_vent_light")
    expect(emergency_alert).not_to_be_visible()


def test_e2e_dangerous_mix_triggers_emergency_alert(page: Page, live_server):
    """
    Verifies that mixing the specific dangerous chemicals correctly updates the
    success log AND triggers the `HX-Trigger` event, making the emergency alert visible.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Select the dangerous combination.
    page.get_by_label("Chemical A").select_option("Acidic Reagent")
    page.get_by_label("Chemical B").select_option("Volatile Catalyst")
    page.get_by_test_id("mix_chemicals_form").get_by_role("button").click()

    # 3. Assert: Verify both the log update and the alert visibility.
    success_log = page.get_by_test_id("reaction_result")
    expect(success_log).to_contain_text("[SUCCESS LOG] Mix complete: Acidic Reagent + Volatile Catalyst formed.")
    
    # The key assertion: the emergency alert is now visible due to the HX-Trigger.
    emergency_alert = page.get_by_test_id("emergency_vent_light")
    expect(emergency_alert).to_be_visible()
    expect(emergency_alert).to_contain_text("EMERGENCY: VENT NOW!")


def test_e2e_risky_experiment_updates_error_log(page: Page, live_server):
    """
    Verifies that clicking the 'Risky Experiment' button, which is designed to fail,
    correctly populates the error log with the message from the 422 response.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the button that triggers a backend error.
    page.get_by_test_id("risky_experiment_button").click()

    # 3. Assert: The error log should now display the backend's error fragment.
    error_log = page.get_by_test_id("error_log")
    expect(error_log).to_contain_text("[ERROR LOG] Unprocessable Entity: Useless brown sludge formed. Experiment failed.")
    
    # The success log should remain in its initial state.
    success_log = page.get_by_test_id("reaction_result")
    expect(success_log).to_contain_text("Awaiting experiment results...")


def test_e2e_temperature_poll_updates_display(page: Page, live_server):
    """
    Verifies that the temperature display, which polls every 5 seconds,
    correctly updates its content when the backend provides a new value.
    """
    # 1. Arrange: Navigate and verify the initial state from the Jinja2 template.
    page.goto("http://127.0.0.1:8000")
    temp_display = page.get_by_test_id("temperature_display")
    expect(temp_display).to_have_text("22°C")

    # 2. Act: Intercept the next network request to `/temperature` and fulfill it
    # with a new, predictable value. This is more reliable than waiting for a real update.
    page.route(re.compile(".*\/temperature"), lambda route: route.fulfill(
        status=200,
        headers={"Content-Type": "text/html"},
        body="99.9°C"
    ))

    # 3. Assert: Playwright's `expect` will wait for the UI to update after the
    # intercepted poll completes, or time out if it doesn't.
    expect(temp_display).to_have_text("99.9°C")