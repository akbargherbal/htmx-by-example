# Principal Frontend Engineer Notes:
# This E2E test suite uses Playwright to verify the complete system from the user's
# perspective. It ensures that the HTMX-powered frontend correctly interacts with the
# live backend service.
# - Test Philosophy: Each test simulates a specific user journey, asserting on the
#   final, visible UI state. This is more robust than just checking for API responses.
# - `data-testid`: We exclusively use `data-testid` attributes for selecting elements.
#   This decouples tests from fragile selectors like CSS classes or text content,
#   making them resilient to cosmetic UI changes.
# - `expect()`: Playwright's `expect` function is used for all assertions. It has
#   built-in auto-waiting, which eliminates the need for manual `sleep()` calls and
#   makes tests more reliable by waiting for the UI to settle.
# - Backend Verification: Assertions check for the *exact* HTML fragments and CSS
#   classes that the backend is known to return. This confirms that the frontend
#   is not just making a request, but is also correctly processing and displaying
#   the backend's response, validating the full integration.

import re
from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_e2e_initial_page_load_shows_correct_state(page: Page, live_server):
    """
    Verifies that the initial page correctly renders the state provided by the backend.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # 2. Assert: Check that each device card shows the correct initial state from the server.
    # This state is defined in `app/main.py`'s `reset_state_for_testing` function.
    expect(page.get_by_test_id("living-room-speaker-initial")).to_contain_text("Playlist: 90s Rock Anthems")
    expect(page.get_by_test_id("kitchen-light-initial")).to_contain_text("Status: On")
    expect(page.get_by_test_id("ambient-temperature-initial")).to_contain_text("22°C")


def test_e2e_set_playlist_updates_speaker_card(page: Page, live_server):
    """
    Tests that entering text and clicking 'Set Playlist' updates only the speaker card
    with the new playlist name and correct styling.
    """
    # 1. Arrange: Navigate to the app and define the new playlist.
    page.goto("http://127.0.0.1:8000")
    new_playlist = "Chill Lo-fi"

    # 2. Act: Fill the input and click the button.
    page.get_by_test_id("playlist-input").fill(new_playlist)
    page.get_by_test_id("set-playlist-button").click()

    # 3. Assert: Verify the speaker card has updated correctly.
    # The backend returns a new card with a `...-after` testid.
    updated_speaker_card = page.get_by_test_id("living-room-speaker-after")
    expect(updated_speaker_card).to_be_visible()
    expect(updated_speaker_card).to_contain_text(f"Playlist: {new_playlist}")
    # Verify the styling from the backend's HTML fragment is applied.
    expect(updated_speaker_card).to_have_class(re.compile(r"ring-green-500"))


def test_e2e_toggle_light_updates_light_card_from_on_to_off(page: Page, live_server):
    """
    Tests that clicking 'Toggle Kitchen Light' updates the light card from On to Off,
    including the status text and styling.
    """
    # 1. Arrange: Navigate to the app. The light starts in the 'On' state.
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("kitchen-light-initial")).to_contain_text("Status: On")

    # 2. Act: Click the toggle button.
    page.get_by_test_id("toggle-light-button").click()

    # 3. Assert: Verify the light card now shows the 'Off' state.
    updated_light_card = page.get_by_test_id("kitchen-light-after")
    expect(updated_light_card).to_be_visible()
    expect(updated_light_card).to_contain_text("Status: Off")
    # Verify the specific "Off" state classes from the backend response.
    expect(updated_light_card).to_have_class(re.compile(r"ring-gray-600"))
    expect(updated_light_card.locator("span.text-red-400")).to_be_visible()


def test_e2e_refresh_all_updates_all_cards_to_current_state(page: Page, live_server):
    """
    Tests that the 'Refresh All' button correctly fetches and displays the
    current state for all devices.
    """
    # 1. Arrange: Navigate and change the state of one device (light to 'Off').
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("toggle-light-button").click()
    # Wait for the first update to complete and verify the change.
    expect(page.get_by_test_id("kitchen-light-after")).to_contain_text("Status: Off")

    # 2. Act: Click the 'Refresh All Statuses' button.
    page.get_by_test_id("refresh-status-button").click()

    # 3. Assert: Verify the entire grid reflects the current state.
    # The speaker and temperature should remain unchanged.
    expect(page.get_by_test_id("living-room-speaker-after")).to_contain_text("Playlist: 90s Rock Anthems")
    expect(page.get_by_test_id("ambient-temperature-after")).to_contain_text("22°C")
    # The light should still be in its new 'Off' state.
    expect(page.get_by_test_id("kitchen-light-after")).to_contain_text("Status: Off")


def test_e2e_temperature_card_polls_for_updates(page: Page, live_server):
    """
    Verifies that the temperature card automatically sends a GET request
    to /temperature due to its `hx-trigger="every 10s"` attribute.
    """
    # 1. Arrange: Navigate to the app.
    page.goto("http://127.0.0.1:8000")

    # 2. Act & Assert: Use Playwright's request interception to wait for the
    #    polling request to be made after the 10-second interval. This proves
    #    the trigger is working without relying on a flaky `sleep`.
    with page.expect_request("**/temperature", timeout=11000) as request_info:
        # The `with` block will wait up to 11 seconds for the request.
        # No action is needed here; we are just waiting for the poll to fire.
        pass

    # Retrieve the request that was caught.
    request = request_info.value
    # Assert that a GET request was indeed made to the correct endpoint.
    assert request.method == "GET"
    assert request.url.endswith("/temperature")