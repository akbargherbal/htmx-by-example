# app/main.py

# This application serves as the backend for a simplified ATM interface,
# demonstrating specific server-side logic for HTMX interactions.
# As a Principal Engineer, my focus is on creating a clear, reliable, and
# testable API that strictly adheres to the defined contract.

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our web service.
app = FastAPI()

# Configure Jinja2 for HTML templating. This allows us to serve dynamic HTML
# pages and fragments from the `app/templates` directory.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# PRINCIPLE: For this educational project, we avoid the complexity of a database.
# State is managed in a simple Python dictionary. This is volatile and will reset
# on application restart, which is acceptable for this scope.
# The state represents the ATM's current status.
APP_STATE = {}

# This is the initial state of our "ATM".
# We define it in a constant to ensure consistency.
INITIAL_STATE = {
    "card_inserted": False,
    "authenticated": False,
    "balance": 1000.00
}

def reset_state_for_testing():
    """
    Resets the application state to its initial default.
    This is a critical utility for ensuring test isolation. By calling this
    before each test, we guarantee that one test's side effects do not
    influence another's outcome.
    """
    global APP_STATE
    APP_STATE = INITIAL_STATE.copy()

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This is the user's entrypoint to the application. It renders the full UI
    and injects the initial state of the ATM into the template context.
    """
    # The context dictionary passes server-side data to the Jinja2 template.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_state": APP_STATE}
    )


# --- API Endpoints (as per contract) ---

@app.post("/login", response_class=HTMLResponse)
async def login(pin: Annotated[str, Form()]):
    """
    Handles the PIN submission to authenticate the user session.
    CONTRACT: This endpoint requires a "card" to be inserted first.
    """
    # This simulates a hardware check: has the user inserted their card?
    # In a real app, this might be a check for a valid session cookie.
    if not APP_STATE["card_inserted"]:
        # Per the contract, if no card is present, we return a 402 error.
        # The status code 402 "Payment Required" is unusual but specified, so we adhere to it.
        html_content = f"""
        <div>
          <p class="text-xl font-bold text-red-400">Error: No Card Inserted</p>
          <p class="text-gray-300 mt-2">Please simulate 'Insert Card' before entering a PIN.</p>
        </div>
        """
        return HTMLResponse(content=html_content, status_code=402)

    # If a card is inserted, we mark the session as authenticated.
    # For this example, any PIN is considered valid.
    APP_STATE["authenticated"] = True
    current_balance = f"${APP_STATE['balance']:.2f}"

    html_content = f"""
    <div>
      <p class="text-xl font-bold text-green-400">Authentication Successful!</p>
      <p class="text-gray-300 mt-2">Current Balance: {current_balance}</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/withdraw", response_class=HTMLResponse)
async def withdraw(amount: Annotated[str, Form()]):
    """
    Handles a withdrawal request.
    CONTRACT: This endpoint validates if the requested amount exceeds the balance.
    """
    try:
        withdrawal_amount = float(amount)
    except (ValueError, TypeError):
        # Robustness: Handle cases where the form data is not a valid number.
        html_content = "<p>Invalid amount entered.</p>"
        return HTMLResponse(content=html_content, status_code=400) # 400 Bad Request

    # Business logic: Check for sufficient funds.
    if withdrawal_amount > APP_STATE["balance"]:
        # Per the contract, return a 403 Forbidden status if funds are insufficient.
        attempted_amount = f"${withdrawal_amount:.2f}"
        current_balance = f"${APP_STATE['balance']:.2f}"
        html_content = f"""
        <div>
          <p class="text-xl font-bold text-red-400">Transaction Failed: Insufficient Funds</p>
          <p class="text-gray-300 mt-2">Attempted to withdraw {attempted_amount}, but balance is only {current_balance}.</p>
        </div>
        """
        return HTMLResponse(content=html_content, status_code=403)

    # On success, update the state and return a success message.
    APP_STATE["balance"] -= withdrawal_amount
    new_balance = f"${APP_STATE['balance']:.2f}"
    html_content = f"""
    <div>
      <p class="text-xl font-bold text-green-400">Withdrawal Successful!</p>
      <p class="text-gray-300 mt-2">New Balance: {new_balance}</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/balance", response_class=HTMLResponse)
async def check_balance():
    """
    Checks the account balance.
    CONTRACT: This endpoint has dual behavior. If the user is authenticated, it
    returns the balance. If not (e.g., session timed out), it triggers a
    client-side redirect via an HX-Redirect header.
    """
    if not APP_STATE["authenticated"]:
        # This simulates a timed-out or unauthenticated session.
        # We return a 200 OK but include a special HTMX header that tells the
        # frontend to navigate to the /home URL.
        # We must use a generic `Response` object to manually set the header.
        return Response(status_code=200, headers={"HX-Redirect": "/home"})

    # If authenticated, return the current balance as an HTML fragment.
    current_balance = f"${APP_STATE['balance']:.2f}"
    html_content = f"""
    <div>
      <p class="text-xl font-bold text-blue-400">Account Balance</p>
      <p class="text-gray-300 mt-2">Your current balance is: {current_balance}</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/home", response_class=HTMLResponse)
async def get_home_screen():
    """
    Serves the content for the 'home' screen.
    CONTRACT: This is the target of the HX-Redirect from the /balance endpoint.
    It provides a generic message prompting the user for action.
    """
    html_content = """
    <p class="text-xl text-gray-400">Please insert your card and enter your PIN using the panels below.</p>
    """
    return HTMLResponse(content=html_content, status_code=200)


# --- Helper Endpoint for Simulation (Not part of the official contract) ---
# This endpoint is included to make the manual browser-based simulation of the
# "insert card" action possible, which is a prerequisite for the /login endpoint.
@app.post("/simulation/insert-card", response_class=HTMLResponse)
async def insert_card():
    """Simulates a user inserting their ATM card."""
    APP_STATE["card_inserted"] = True
    APP_STATE["authenticated"] = False # Inserting a card resets authentication
    return HTMLResponse(content="<p>Card Inserted. Please enter PIN.</p>")

@app.post("/simulation/remove-card", response_class=HTMLResponse)
async def remove_card():
    """Simulates a user removing their ATM card, resetting the session."""
    reset_state_for_testing() # The simplest way to reset is to use the test utility
    return HTMLResponse(content="<p>Card removed. Thank you.</p>")