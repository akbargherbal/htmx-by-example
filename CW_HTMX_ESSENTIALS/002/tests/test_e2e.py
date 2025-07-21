# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) tests for the Stage Manager UI.
#
# Key Testing Principles Applied:
# 1.  User-Centric Scenarios: Each test function simulates a distinct user journey,
#     like changing the set or ordering a prop. This makes tests readable and tied
#     to actual features.
# 2.  `data-testid` Selectors: All element selections use `page.get_by_test_id()`.
#     This is non-negotiable for creating robust tests that are decoupled from
#     fragile selectors like CSS classes or element structure.
# 3.  `expect` for Assertions: Playwright's `expect()` is used for all assertions.
#     Its auto-waiting capability eliminates the need for manual waits (`time.sleep`)
#     and makes the tests more reliable.
# 4.  Asserting on Backend Truth: The assertions check for the *exact* HTML content
#     and attributes that the backend (`app/main.py`) is known to return. For example,
#     we don't just check for "a new div", we check for the div with
#     `data-testid="fireplace-after"` because that's what the API provides. This
#     ensures we are testing the full, integrated system correctly.

from playwright.sync_api import Page, expect
import re  # Import regex module for class assertions

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.


def test_e2e_set_changes_update_the_stage(page: Page, live_server):
    """
    Verifies that clicking the various 'Set Change' buttons correctly updates
    the stage using different hx-swap strategies (innerHTML, outerHTML, etc.).
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Act & Assert: Change Backdrop (innerHTML)
    page.get_by_test_id("change-backdrop-btn").click()
    # The img inside the frame should be replaced.
    backdrop_img = page.locator("#backdrop-frame img")
    expect(backdrop_img).to_have_attribute("alt", "A stormy sea painting")
    expect(backdrop_img).to_have_attribute("src", re.compile("Stormy\\+Sea"))

    # 3. Act & Assert: Replace Fireplace (outerHTML)
    # The initial fireplace should no longer be present.
    expect(page.get_by_test_id("fireplace-initial")).to_be_visible()
    page.get_by_test_id("replace-fireplace-btn").click()
    # The new fireplace from the server, with its own test-id, should be visible.
    expect(page.get_by_test_id("fireplace-initial")).not_to_be_visible()
    expect(page.get_by_test_id("fireplace-after")).to_be_visible()
    expect(page.get_by_test_id("fireplace-after")).to_contain_text("Modern Hearth")

    # 4. Act & Assert: Add Chair (beforeend)
    # We click the button that adds a chair directly first to ensure it works.
    page.get_by_test_id("add-chair-btn").click()
    # The new chair prop should appear inside the #stage div.
    expect(page.get_by_test_id("chair-prop")).to_be_visible()
    expect(page.get_by_test_id("chair-prop")).to_contain_text("New Chair")

    # 5. Act & Assert: Add Coat Rack (afterend)
    page.get_by_test_id("add-coat-rack-btn").click()
    # The coat rack should appear *after* the #stage div, so we check it's visible on the page.
    expect(page.get_by_test_id("coat-rack-prop")).to_be_visible()
    expect(page.get_by_test_id("coat-rack-prop")).to_contain_text("Coat Rack")


def test_e2e_hx_select_adds_only_the_correct_prop(page: Page, live_server):
    """
    Verifies that using hx-select correctly extracts only the desired element
    from the server's full HTML response and appends it to the stage.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    # Ensure the telephone is not on the stage initially.
    expect(page.locator("#antique-telephone")).not_to_be_visible()

    # 2. Act
    page.get_by_test_id("get-telephone-btn").click()

    # 3. Assert
    # The telephone should now be on the stage.
    telephone_prop = page.locator("#antique-telephone")
    expect(telephone_prop).to_be_visible()
    expect(telephone_prop).to_contain_text("Antique Telephone")
    # Crucially, other items from the server response should NOT be present.
    expect(page.locator("#fancy-vase")).not_to_be_visible()
    expect(page.locator("#grandfather-clock")).not_to_be_visible()


def test_e2e_form_submission_replaces_form_with_confirmation(page: Page, live_server):
    """
    Verifies that submitting the workshop form with hx-post replaces the form
    element with the confirmation message from the server.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    # The form should be visible initially.
    expect(page.get_by_test_id("workshop-order-form")).to_be_visible()
    expect(page.get_by_test_id("workshop-confirmation")).not_to_be_visible()

    # 2. Act: Click the submit button within the form.
    page.get_by_test_id("request-set-piece-btn").click()

    # 3. Assert
    # The form should now be gone.
    expect(page.get_by_test_id("workshop-order-form")).not_to_be_visible()
    # The confirmation message should be visible and contain the correct data.
    confirmation_message = page.get_by_test_id("workshop-confirmation")
    expect(confirmation_message).to_be_visible()
    expect(confirmation_message).to_contain_text(
        "Confirmed: New set piece ordered for stage (800x600)."
    )


def test_e2e_hx_trigger_updates_effects_boards(page: Page, live_server):
    """
    Verifies that a server response with an HX-Trigger header correctly
    fires client-side events that are handled by AlpineJS.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    lighting_board_status = page.get_by_test_id("lighting-board-status-initial")
    sound_board_status = page.get_by_test_id("sound-board-status-initial")

    # Assert initial state
    expect(lighting_board_status).to_contain_text("-- IDLE --")
    expect(lighting_board_status).to_have_class(re.compile(r"text-gray-600"))
    expect(sound_board_status).to_contain_text("-- IDLE --")
    expect(sound_board_status).to_have_class(re.compile(r"text-gray-600"))

    # 2. Act
    page.get_by_test_id("cue-effects-btn").click()

    # 3. Assert: Verify the UI has updated based on the custom event.
    # The AlpineJS component should have heard the events and updated the text and classes.
    expect(lighting_board_status).to_contain_text("⚡ FLASHING ⚡")
    expect(lighting_board_status).to_have_class(
        re.compile(r"text-yellow-400 animate-pulse")
    )
    expect(sound_board_status).to_contain_text("🔊 THUNDER 🔊")
    expect(sound_board_status).to_have_class(re.compile(r"text-blue-400"))
