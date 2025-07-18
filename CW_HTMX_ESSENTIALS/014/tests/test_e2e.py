# Principal Frontend Engineer Notes:
# This E2E test suite uses Playwright to verify the complete user-facing system.
# It simulates user actions on the frontend and asserts that the UI updates correctly
# based on the *exact* HTML fragments returned by the live backend.
#
# Key Testing Principles Applied:
# 1.  User-Centric Scenarios: Each test function represents a distinct user journey,
#     like "install an item" or "order a cabinet".
# 2.  `data-testid` Selectors: All element selections use `data-testid` attributes. This
#     decouples the tests from fragile CSS classes or HTML structure, making them
#     more resilient to cosmetic changes.
# 3.  `expect` for Assertions: Playwright's `expect` function is used for all assertions.
#     It has built-in auto-waiting, which eliminates the need for manual `sleep()` calls
#     and makes the tests more reliable.
# 4.  Backend Contract Verification: The assertions check for the specific content,
#     attributes, and structure that the `app/main.py` backend is known to produce. This
#     ensures we are testing the true integration, not just a mocked frontend.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_install_item_with_default_swap_updates_window(page: Page, live_server):
    """
    Verifies that clicking 'Install Item' with the default 'innerHTML' swap
    correctly places the new item inside the target window frame.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # Locate the target area and assert its initial placeholder state.
    target_area = page.get_by_test_id("window-frame-after-inner")
    expect(target_area).to_have_text("Result will appear here.")

    # 2. Act: Simulate the user clicking the install button.
    page.get_by_test_id("install-item-button").click()

    # 3. Assert: Verify the UI has updated with the precise HTML from the backend.
    # The new item should now be visible inside the target area.
    new_item = target_area.get_by_test_id("new-item-1")
    expect(new_item).to_be_visible()
    expect(new_item).to_have_text("A shiny new glass pane")
    # Verify class to ensure styles are applied, confirming the full fragment was swapped.
    expect(new_item).to_have_class("bg-cyan-900/50 text-cyan-300 p-6 rounded text-center")


def test_install_item_with_outerhtml_swap_replaces_window(page: Page, live_server):
    """
    Verifies that changing the swap style to 'outerHTML' correctly *replaces*
    the target element with the new item from the server.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    original_target = page.get_by_test_id("window-frame-after-inner")
    expect(original_target).to_be_visible() # Ensure it exists before the swap.

    # 2. Act
    # Change the swap style using the dropdown.
    page.get_by_test_id("swap-style-selector").select_option("outerHTML")
    # Click the button to trigger the swap.
    page.get_by_test_id("install-item-button").click()

    # 3. Assert
    # The original target element should no longer exist in the DOM.
    expect(original_target).not_to_be_attached()

    # The new item should now exist in the DOM, but not inside the old target.
    # We find it within the parent container of the original target.
    parent_container = page.get_by_test_id("swap-demo-area-after")
    new_item = parent_container.get_by_test_id("new-item-1")
    expect(new_item).to_be_visible()
    expect(new_item).to_have_text("A shiny new glass pane")


def test_fetch_doorknob_with_select_updates_door(page: Page, live_server):
    """
    Verifies that using `hx-select` correctly extracts just the doorknob
    from the full door assembly response and places it in the target div.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    target_area = page.get_by_test_id("door-after")
    expect(target_area).to_have_text("Result will appear here.")

    # 2. Act
    page.get_by_test_id("fetch-doorknob-button").click()

    # 3. Assert
    # The target should now contain ONLY the text from the selected span.
    expect(target_area).to_have_text("A brass doorknob")
    # Crucially, assert that other parts of the server response were NOT included.
    expect(target_area).not_to_contain_text("A sturdy oak door panel.")
    expect(target_area).not_to_contain_text("Two iron hinges.")


def test_order_cabinet_with_include_updates_wall(page: Page, live_server):
    """
    Verifies that using `hx-include` correctly sends form data (the width)
    to the server and swaps the dynamically generated response into the target.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    target_area = page.get_by_test_id("empty-wall-after")
    expect(target_area).to_have_text("Result will appear here.")
    input_width = "165cm"

    # 2. Act
    # Fill the input field with a specific value.
    page.get_by_test_id("wall-width-input").fill(input_width)
    # Click the button to submit the form data via hx-include.
    page.get_by_test_id("order-cabinet-button").click()

    # 3. Assert
    # Find the new cabinet element that was created by the backend.
    new_cabinet = target_area.get_by_test_id("custom-cabinet")
    expect(new_cabinet).to_be_visible()
    # Verify that the text content reflects the submitted width.
    expect(new_cabinet).to_have_text(f"Custom Cabinet (Width: {input_width})")
    # Verify that the style attribute was dynamically generated with the correct width.
    expect(new_cabinet).to_have_attribute("style", f"width: {input_width}; max-width: 100%;")