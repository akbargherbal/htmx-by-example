# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) test suite using Playwright.
#
# Testing Philosophy:
# Our E2E tests are the ultimate proof that the system works as a whole. They simulate real user journeys,
# from clicking a button to seeing the final UI update. We are not just testing the frontend in isolation;
# we are verifying the complete integration between the HTMX-powered HTML and the live FastAPI backend.
#
# Key Principles Embodied in This Suite:
# 1. User-Centric Scenarios: Each test function is named to describe a specific user action and its expected outcome.
# 2. `data-testid` Selectors: We exclusively use `data-testid` attributes for selecting elements. This decouples our
#    tests from fragile implementation details like CSS classes or element structure, making them robust and maintainable.
# 3. `expect` for Assertions: Playwright's `expect()` function is used for all assertions. It has built-in
#    auto-waiting, which eliminates the need for manual `sleep()` calls and makes our tests more reliable by waiting
#    for the UI to reach the expected state after an HTMX request completes.
# 4. Asserting Against Backend Truth: The assertions verify that the UI displays the *exact* HTML fragments
#    that we know the backend (`app/main.py`) returns. This confirms that the frontend is correctly interpreting
#    and rendering the API's responses.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by conftest.py
# The `page` fixture is automatically provided by pytest-playwright.

def test_successful_registration_replaces_content(page: Page, live_server):
    """
    Verifies that clicking the successful registration button replaces the main
    content area with the schedule confirmation, as returned by the backend.
    """
    # 1. Arrange: Navigate to the running application's main page.
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("main-content-initial")).to_be_visible()

    # 2. Act: Simulate the user clicking the "Register for BIOL-101" button.
    page.get_by_test_id("register-biol-101-btn").click()

    # 3. Assert: Verify the UI has updated correctly.
    # The initial content should now be gone.
    expect(page.get_by_test_id("main-content-initial")).not_to_be_visible()
    
    # The new content, with its specific test-id from the backend, should be visible.
    success_content = page.get_by_test_id("main-content-after-success")
    expect(success_content).to_be_visible()
    expect(success_content).to_contain_text("My Fall Schedule")
    expect(success_content).to_contain_text("BIOL-101: Introduction to Biology")
    
    # Verify that hx-push-url worked as expected.
    expect(page).to_have_url("http://127.0.0.1:8000/register/success")


def test_full_course_registration_shows_inline_error(page: Page, live_server):
    """
    Verifies that attempting to register for a full course displays an inline
    error message next to the button without replacing the whole page.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    # The error display area should initially be empty.
    expect(page.get_by_test_id("registration-error-target")).to_be_empty()

    # 2. Act
    page.get_by_test_id("register-hist-350-btn").click()

    # 3. Assert
    # The error message from the backend should now be rendered inside the target div.
    error_target = page.get_by_test_id("registration-error-target")
    error_content = error_target.get_by_test_id("registration-error-target-after-action")
    expect(error_content).to_be_visible()
    expect(error_content).to_contain_text("Error: Course is full.")


def test_forbidden_request_shows_403_error_in_results_area(page: Page, live_server):
    """
    Verifies that a 403 Forbidden response from the server is correctly
    rendered in the designated results display area.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("records-result-target")).to_contain_text("Results will be displayed here...")

    # 2. Act
    page.get_by_test_id("get-grades-forbidden-btn").click()

    # 3. Assert
    result_area = page.get_by_test_id("records-result-target")
    error_content = result_area.get_by_test_id("records-result-target-after-403")
    expect(error_content).to_be_visible()
    expect(error_content).to_contain_text("Access Denied (403 Forbidden)")


def test_not_found_request_shows_404_error_in_results_area(page: Page, live_server):
    """
    Verifies that a 404 Not Found response from the server is correctly
    rendered in the designated results display area.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("records-result-target")).to_contain_text("Results will be displayed here...")

    # 2. Act
    page.get_by_test_id("get-transcript-not-found-btn").click()

    # 3. Assert
    result_area = page.get_by_test_id("records-result-target")
    error_content = result_area.get_by_test_id("records-result-target-after-404")
    expect(error_content).to_be_visible()
    expect(error_content).to_contain_text("Not Found (404)")
    expect(error_content).to_contain_text("The requested transcript for the specified student ID does not exist.")


def test_redirect_header_navigates_to_tuition_page(page: Page, live_server):
    """
    Verifies that a response with an HX-Redirect header correctly navigates
    the browser to the new page, replacing the content entirely.
    """
    # 1. Arrange
    page.goto("http://127.0.0.1:8000")
    expect(page.get_by_test_id("main-content-initial")).to_be_visible()

    # 2. Act
    page.get_by_test_id("get-grades-redirect-btn").click()

    # 3. Assert
    # The browser should navigate, so the old content is gone.
    expect(page.get_by_test_id("main-content-initial")).not_to_be_visible()
    
    # The new page content from the redirect target should be visible.
    redirect_content = page.get_by_test_id("main-content-after-redirect")
    expect(redirect_content).to_be_visible()
    expect(redirect_content).to_contain_text("Tuition Payment Required")
    
    # The browser URL should have changed to the redirect destination.
    expect(page).to_have_url("http://127.0.0.1:8000/pay-tuition")