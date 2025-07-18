# Principal Frontend Engineer Notes:
# This file contains the end-to-end (E2E) test suite for the ATM application.
# The tests use Playwright to simulate real user interactions in a browser, verifying that
# the HTMX-powered frontend correctly integrates with the FastAPI backend.
#
# Key Testing Principles Followed:
# 1. User-Centric Scenarios: Each test function represents a complete user journey,
#    such as "log in successfully" or "fail to withdraw due to insufficient funds."
# 2. `data-testid` Selectors: All element selections are made using `data-testid` attributes.
#    This is a best practice that decouples tests from fragile CSS classes or HTML structure.
# 3. `expect` Assertions: Playwright's `expect` function is used for all assertions. It has
#    built-in auto-waiting, which makes the tests robust against minor network or rendering delays.
# 4. Verification of True Backend Output: The assertions check for the *exact* HTML fragments
#    that the backend (`app/main.py`) is known to produce, ensuring a true integration test.

from playwright.sync_api import Page, expect

# The `live_server` fixture is automatically provided by `conftest.py`.
# The `page` fixture is automatically provided by `pytest-playwright`.

def test_e2e_successful_login(page: Page, live_server):
    """
    Verifies the full user journey for a successful login.
    1. User inserts card (simulation).
    2. User enters a PIN and submits.
    3. The ATM screen updates with the success message and balance.
    """
    # 1. Arrange: Navigate to the app and simulate inserting a card.
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-card-button").click()

    # 2. Act: Fill in the PIN and click the submit button.
    page.get_by_test_id("pin-input").fill("1234")
    page.get_by_test_id("pin-submit-button").click()

    # 3. Assert: Verify the UI has updated with the exact success message from the backend.
    atm_screen = page.get_by_test_id("atm-screen")
    expect(atm_screen.get_by_text("Authentication Successful!")).to_be_visible()
    expect(atm_screen.get_by_text("Current Balance: $1000.00")).to_be_visible()

def test_e2e_login_fails_if_no_card_is_inserted(page: Page, live_server):
    """
    Verifies that attempting to log in without first "inserting a card"
    results in the correct error message on the screen.
    """
    # 1. Arrange: Navigate to the app. Do NOT simulate inserting a card.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Attempt to log in.
    page.get_by_test_id("pin-input").fill("1234")
    page.get_by_test_id("pin-submit-button").click()

    # 3. Assert: Verify the UI shows the "No Card Inserted" error.
    atm_screen = page.get_by_test_id("atm-screen")
    expect(atm_screen.get_by_text("Error: No Card Inserted")).to_be_visible()
    expect(atm_screen.get_by_text("Please simulate 'Insert Card' before entering a PIN.")).to_be_visible()

def test_e2e_successful_withdrawal(page: Page, live_server):
    """
    Verifies that after logging in, a valid withdrawal updates the balance correctly.
    """
    # 1. Arrange: Navigate, insert card, and log in to establish an authenticated session.
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-card-button").click()
    page.get_by_test_id("pin-input").fill("1234")
    page.get_by_test_id("pin-submit-button").click()

    # 2. Act: Enter a withdrawal amount and submit.
    page.get_by_test_id("withdrawal-amount-input").fill("200")
    page.get_by_test_id("withdraw-button").click()

    # 3. Assert: Verify the UI shows the withdrawal success message and the new balance.
    atm_screen = page.get_by_test_id("atm-screen")
    expect(atm_screen.get_by_text("Withdrawal Successful!")).to_be_visible()
    expect(atm_screen.get_by_text("New Balance: $800.00")).to_be_visible()

def test_e2e_withdrawal_fails_for_insufficient_funds(page: Page, live_server):
    """
    Verifies that attempting to withdraw more than the available balance
    results in the correct "Insufficient Funds" error message.
    """
    # 1. Arrange: Log in to establish an authenticated session.
    page.goto("http://127.0.0.1:8000")
    page.get_by_test_id("insert-card-button").click()
    page.get_by_test_id("pin-input").fill("1234")
    page.get_by_test_id("pin-submit-button").click()

    # 2. Act: Attempt to withdraw an amount greater than the initial balance.
    page.get_by_test_id("withdrawal-amount-input").fill("5000")
    page.get_by_test_id("withdraw-button").click()

    # 3. Assert: Verify the specific error message is displayed.
    atm_screen = page.get_by_test_id("atm-screen")
    expect(atm_screen.get_by_text("Transaction Failed: Insufficient Funds")).to_be_visible()
    expect(atm_screen.get_by_text("Attempted to withdraw $5000.00, but balance is only $1000.00.")).to_be_visible()

def test_e2e_check_balance_redirects_when_not_authenticated(page: Page, live_server):
    """
    Verifies that clicking "Check Balance" without being logged in triggers the
    HX-Redirect flow, ultimately displaying the home screen message.
    """
    # 1. Arrange: Navigate to the app. Do not log in.
    page.goto("http://127.0.0.1:8000")

    # 2. Act: Click the "Check Balance" button.
    page.get_by_test_id("check-balance-button").click()

    # 3. Assert: Verify the screen content is the result of the redirect to /home.
    # Playwright's auto-waiting handles the time taken for the redirect and subsequent swap.
    atm_screen = page.get_by_test_id("atm-screen")
    expect(atm_screen.get_by_text("Please insert your card and enter your PIN using the panels below.")).to_be_visible()