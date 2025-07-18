# This comment explains the purpose of the E2E test file.
# It uses Playwright to simulate real user interactions and
# verifies that the UI updates with the exact content from the backend.
# As a Principal, I ensure tests are readable, robust, and test the user journey, not just isolated units.

from playwright.sync_api import Page, expect
from app.main import HEADLINES, BREAKING_STORY

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_e2e_breaking_news_event_updates_main_screen(page: Page, live_server):
    """
    Verifies the event-driven update flow.
    1. User clicks the "SEND...ALERT" button.
    2. The button's POST request returns an `HX-Trigger` header.
    3. The main screen div, listening for this event, fetches and displays the breaking news story.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Verify the main screen is in its default state.
    main_screen = page.get_by_test_id("main-screen-content")
    expect(main_screen).to_contain_text("Awaiting broadcast...")

    # 3. Act: Simulate the user clicking the button that triggers the event.
    page.get_by_test_id("send-alert-button").click()

    # 4. Assert Final State: Verify the main screen has been updated with the breaking news.
    # Playwright's `expect` has built-in auto-waiting, so we don't need manual sleeps.
    # We assert for the exact content we know the backend's `/api/story/breaking` endpoint returns.
    expect(main_screen).to_contain_text("BREAKING NEWS")
    expect(main_screen).to_contain_text(BREAKING_STORY)
    expect(main_screen).not_to_contain_text("Awaiting broadcast...")

def test_e2e_coordinated_update_swaps_main_screen_and_sidebar_oob(page: Page, live_server):
    """
    Verifies the Out-of-Band (OOB) swap flow.
    1. User clicks the "Send Coordinated Update" button.
    2. The backend returns a single response with two HTML fragments.
    3. The main fragment updates the main screen (the button's target).
    4. The OOB fragment updates the sidebar list, which has a matching ID.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Check the content of both the main screen and the sidebar.
    main_screen = page.get_by_test_id("main-screen-content")
    sidebar_list = page.get_by_test_id("alerts-sidebar-list")
    expect(main_screen).to_contain_text("Awaiting broadcast...")
    expect(sidebar_list).to_contain_text("System Initialized")
    expect(sidebar_list).not_to_contain_text("Coordinated Update Received")

    # 3. Act: Click the button that triggers the coordinated update.
    page.get_by_test_id("send-coordinated-update-button").click()

    # 4. Assert Final State: Verify both elements have been updated.
    # Assert the main screen content changed.
    expect(main_screen).to_contain_text("BREAKING NEWS")
    expect(main_screen).to_contain_text(BREAKING_STORY)

    # Assert the sidebar was updated via OOB swap. The backend returns the *entire* new list,
    # so we must check that both the old and new items are present.
    expect(sidebar_list).to_contain_text("System Initialized")
    expect(sidebar_list).to_contain_text("Coordinated Update Received")

def test_e2e_news_ticker_polls_for_new_headlines(page: Page, live_server):
    """
    Verifies the declarative polling mechanism.
    1. The page loads with an initial, static headline in the ticker.
    2. The ticker div has an `hx-trigger` attribute to poll every 2 seconds.
    3. The test waits and confirms that the content of the ticker is automatically replaced.
    """
    # 1. Arrange: Navigate to the page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert Initial State: Get the ticker element and its initial text.
    news_ticker = page.get_by_test_id("news-ticker-content")
    initial_text = "Weather: Sunny skies expected all week in the metropolitan area..."
    expect(news_ticker).to_contain_text(initial_text)

    # 3. Assert Final State (after polling):
    # We use `not_to_contain_text` with the initial text. `expect` will wait for a
    # specified timeout for the condition to become true, which is perfect for testing polling.
    expect(news_ticker).not_to_contain_text(initial_text, timeout=3000)

    # Now, verify it contains the *first* headline from the backend's list,
    # which is what the polling mechanism will fetch first.
    expect(news_ticker).to_contain_text(HEADLINES[0])