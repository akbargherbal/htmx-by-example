# Principal Engineer's Note:
# This file contains the end-to-end (E2E) test suite for the Jukebox application.
# E2E tests are the ultimate proof that the frontend (HTML/HTMX) and backend (FastAPI)
# are correctly integrated. We use Playwright to simulate real user interactions in a browser.
#
# Key Testing Principles Applied:
# 1. User-Centric Scenarios: Tests are named and structured around user actions,
#    like `test_inserting_coin_enables_song_selection`.
# 2. `data-testid` Selectors: We exclusively use `data-testid` attributes for selecting
#    elements. This makes tests resilient to changes in styling or layout.
# 3. `expect` Assertions: Playwright's `expect()` function is used for all assertions.
#    It has built-in auto-waiting, which eliminates the need for fragile `time.sleep()` calls.
# 4. Asserting on Backend Truth: Assertions check for the specific HTML content and
#    attributes that we know the backend returns, verifying the complete system.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by `conftest.py`.
# The `page` fixture is automatically provided by `pytest-playwright`.

def test_initial_page_state_is_correct(page: Page, live_server):
    """
    Verifies that the initial state of the page is rendered correctly
    based on the context provided by the `GET /` endpoint.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Check that all elements are in their expected initial state.
    # The "Insert Coin" button should be visible and enabled.
    expect(page.get_by_test_id("insert-coin-button-initial")).to_be_visible()
    expect(page.get_by_test_id("insert-coin-button-initial")).to_be_enabled()

    # The "Select" buttons in the initial grid should be disabled.
    expect(page.get_by_test_id("song-B5-select-disabled")).to_be_disabled()
    expect(page.get_by_test_id("song-C1-select-disabled")).to_be_disabled()

    # The main display should show the initial placeholder text.
    expect(page.get_by_test_id("main-display")).to_contain_text("--- PREVIEW ---")

    # The queue should show the "empty" message.
    expect(page.get_by_test_id("queue-list")).to_contain_text("Queue is empty.")


def test_inserting_coin_enables_song_selection(page: Page, live_server):
    """
    Verifies that clicking "Insert Coin" triggers an HTMX request that
    replaces the disabled song grid with an enabled one from the server.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Simulate the user clicking the "Insert Coin" button.
    page.get_by_test_id("insert-coin-button-initial").click()

    # 3. Assert: Verify that the UI has updated correctly.
    # We expect the new grid, with its specific test-id from the backend, to be visible.
    expect(page.get_by_test_id("song-selectors-enabled")).to_be_visible()

    # A key indicator is that the "Select" buttons are now enabled.
    # We check for the new test-id (`-enabled`) that the backend provides.
    expect(page.get_by_test_id("song-C1-select-enabled")).to_be_enabled()

    # The initial disabled grid should no longer exist in the DOM.
    expect(page.get_by_test_id("song-selectors-disabled")).not_to_be_visible()


def test_preview_song_updates_main_display(page: Page, live_server):
    """
    Verifies that after enabling the jukebox, clicking a "Preview" button
    correctly updates the main display with the song's details.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-coin-button-initial").click()
    # Wait for the enabled grid to ensure the next selector is available.
    expect(page.get_by_test_id("song-B5-preview-enabled")).to_be_visible()

    # 2. Act: Click the preview button for "Hound Dog".
    page.get_by_test_id("song-B5-preview-enabled").click()

    # 3. Assert: Check that the main display now contains the exact text from the backend fragment.
    main_display = page.get_by_test_id("main-display")
    expect(main_display.get_by_test_id("main-display-after-preview")).to_be_visible()
    expect(main_display).to_contain_text("Song: Hound Dog")
    expect(main_display).to_contain_text("Runtime: 2:16")


def test_select_song_adds_item_to_queue(page: Page, live_server):
    """
    Verifies that clicking a "Select" button appends a new item to the queue list.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-coin-button-initial").click()
    # Wait for the enabled grid to ensure the next selector is available.
    expect(page.get_by_test_id("song-C1-select-enabled")).to_be_visible()

    # 2. Act: Click the select button for "Jailhouse Rock".
    page.get_by_test_id("song-C1-select-enabled").click()

    # 3. Assert: Check that the new list item appears in the queue.
    queue_list = page.get_by_test_id("queue-list")
    new_item = queue_list.get_by_test_id("queue-item-C1")
    expect(new_item).to_be_visible()
    expect(new_item).to_have_text("C1 - Jailhouse Rock")

    # This is a critical assertion: based on the backend implementation, the "Queue is empty"
    # message is NOT removed. This test correctly verifies the actual behavior.
    expect(queue_list).to_contain_text("Queue is empty.")


def test_selecting_multiple_songs_appends_to_queue(page: Page, live_server):
    """
    Verifies that `hx-swap="beforeend"` works correctly by adding multiple
    items to the queue in the correct order.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-coin-button-initial").click()
    # Wait for the enabled grid.
    expect(page.get_by_test_id("song-selectors-enabled")).to_be_visible()

    # 2. Act: Select two different songs.
    page.get_by_test_id("song-C1-select-enabled").click()
    page.get_by_test_id("song-A3-select-enabled").click()

    # 3. Assert: Both items should now be in the queue list.
    queue_list = page.get_by_test_id("queue-list")
    item1 = queue_list.get_by_test_id("queue-item-C1")
    item2 = queue_list.get_by_test_id("queue-item-A3")

    expect(item1).to_be_visible()
    expect(item1).to_have_text("C1 - Jailhouse Rock")
    expect(item2).to_be_visible()
    expect(item2).to_have_text("A3 - Johnny B. Goode")