# Principal Frontend Engineer Notes:
#
# This file contains the end-to-end (E2E) tests for the library application.
# E2E tests are the ultimate proof that the frontend (HTML/HTMX) and backend (FastAPI)
# are correctly integrated and deliver the expected user experience.
#
# Key Testing Principles Applied:
# 1.  User-Centric Scenarios: The test simulates a real user journey: loading the page,
#     filling out the form, and seeing the result.
# 2.  `data-testid` Selectors: All element selections use `data-testid` attributes. This
#     is the most robust strategy, as it decouples tests from fragile selectors like
#     CSS classes or element structure, which may change for styling reasons.
# 3.  `expect` for Assertions: Playwright's `expect` function is used for all assertions.
#     It has built-in auto-waiting, which eliminates the need for manual `sleep()` calls
#     and makes tests more reliable by waiting for the UI to reach the expected state.
# 4.  Verifying the "Ground Truth": The assertions check for the specific HTML content
#     that we know the backend's `_generate_book_response_html` function produces. This
#     ensures we are testing the true, complete system integration.

from playwright.sync_api import Page, expect
import re

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_form_submission_updates_ui_and_url(page: Page, live_server):
    """
    Verifies the complete user flow:
    1. The page loads in its initial state.
    2. The user fills out and submits the book request form.
    3. The UI updates with the success message from the server.
    4. The browser URL is updated by the HX-Push-Url header.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")

    # Assert Initial State: Before any action, verify the initial "awaiting" message is visible.
    # This confirms the Jinja2 template's `else` block rendered correctly.
    initial_state = page.get_by_test_id("librarian-desk-response-initial")
    expect(initial_state).to_be_visible()
    expect(initial_state).to_contain_text("Awaiting your request...")

    # 2. Act: Simulate the user filling the form and clicking the submit button.
    title_to_request = "The Lost Manuscript"
    author_to_request = "Alex Writer"
    page.get_by_test_id("title-input").fill(title_to_request)
    page.get_by_test_id("author-input").fill(author_to_request)
    page.get_by_test_id("submit-button").click()

    # 3. Assert: Verify the UI and URL have updated correctly after the HTMX swap.

    # Assert URL Update: The backend sends an `HX-Push-Url` header. We must verify
    # that the browser's URL has changed accordingly. The expected slug is a
    # lowercased, hyphenated version of the title.
    expected_slug = "the-lost-manuscript"
    # Use a regular expression to match the URL, as the base URL might vary.
    expect(page).to_have_url(re.compile(f"/book/{expected_slug}$"))

    # Assert UI Update: The initial div should be gone, and the new one should be present.
    # We locate the new element by the `data-testid` that the backend includes in its response.
    final_state = page.get_by_test_id("librarian-desk-response-final")
    expect(final_state).to_be_visible()

    # Assert Content: Check that the content of the new element matches the
    # HTML fragment returned by the server, including the submitted data.
    expect(final_state).to_contain_text("Request Fulfilled!")
    expect(final_state).to_contain_text(f'The book "{title_to_request}" by "{author_to_request}" is now available for you.')
    expect(final_state).to_contain_text(f"/book/{expected_slug}")

    # Assert that the initial state element is no longer on the page.
    expect(page.get_by_test_id("librarian-desk-response-initial")).not_to_be_visible()