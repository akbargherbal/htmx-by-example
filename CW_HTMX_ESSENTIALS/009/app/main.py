# This file implements a FastAPI backend for a virtual vending machine.
# It demonstrates core backend concepts for handling HTMX-driven interactions,
# such as returning HTML fragments, handling state, and using Out-Of-Band swaps.

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict

# --- Application Setup ---

# As a Principal Engineer, I advocate for clear separation of concerns.
# The FastAPI instance is our core application object.
app = FastAPI()

# Jinja2Templates is used to render the main HTML page from a template file.
# This is standard practice for serving the initial UI.
templates = Jinja2Templates(directory="app/templates")


# --- State Management ---

# For this educational project, we use simple in-memory variables for state.
# This is explicitly required to keep the focus on HTMX and API interactions,
# avoiding database complexity. In a real-world application, this data
# would live in a database (e.g., PostgreSQL, Redis).

class Item(BaseModel):
    """A Pydantic model to structure item data, ensuring type safety."""
    name: str
    price: float
    calories: int
    sodium: int
    stock: int

# The global state variables. `ITEMS` acts as our in-memory "database table".
# `credit` tracks the user's current balance.
ITEMS: Dict[str, Item] = {}
credit: float = 0.0
retrieved_items: list[str] = []

def reset_state_for_testing():
    """
    Resets the application's state to its initial condition.
    This is a critical function for ensuring test isolation. Each test run
    should start from a clean, predictable state.
    """
    global credit, ITEMS, retrieved_items
    credit = 0.0
    retrieved_items = []
    ITEMS = {
        "A1": Item(name="Crispy Chips", price=0.75, calories=150, sodium=200, stock=5),
        "B2": Item(name="NutriBar", price=1.25, calories=200, sodium=110, stock=0), # Explicitly sold out for testing
        "C3": Item(name="Soda Pop", price=1.00, calories=180, sodium=30, stock=8),
        "D4": Item(name="Candy Bar", price=0.50, calories=250, sodium=80, stock=10),
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Helper Functions ---

def _render_item_grid_html(current_credit: float) -> str:
    """
    Generates the HTML for the item grid based on the current credit.
    This helper function promotes DRY (Don't Repeat Yourself) by being callable
    from both the root endpoint and the /add-credit endpoint.
    """
    item_html_parts = []
    # Sort items by key for a consistent display order.
    for item_id, item in sorted(ITEMS.items()):
        is_affordable = current_credit >= item.price
        is_sold_out = item.stock <= 0

        if is_sold_out:
            button_html = f"""
            <button class="w-full bg-red-800 text-gray-400 font-bold py-2 px-4 rounded-lg cursor-not-allowed"
                    data-testid="item_selection_button-{item_id}-sold-out">
                SOLD OUT
            </button>
            """
        elif is_affordable:
            button_html = f"""
            <button class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
                    hx-post="/purchase/{item_id}"
                    hx-target="body"
                    hx-swap="none"
                    data-testid="item_selection_button-{item_id}-enabled">
                Purchase
            </button>
            """
        else: # Not sold out, but unaffordable
            button_html = f"""
            <button class="w-full bg-gray-600 text-gray-400 font-bold py-2 px-4 rounded-lg cursor-not-allowed"
                    data-testid="item_selection_button-{item_id}-unaffordable">
                Purchase
            </button>
            """

        item_html_parts.append(f"""
        <div hx-get="/item-info/{item_id}"
             hx-target="#display-screen-target"
             hx-swap="innerHTML"
             class="bg-gray-700 p-4 rounded-lg flex flex-col items-center space-y-2 text-center cursor-pointer hover:bg-gray-600"
             data-testid="item_info_button-{item_id}">
            <p class="font-bold">{item_id}: {item.name}</p>
            <p class="text-sm text-gray-400">${item.price:.2f}</p>
            {button_html}
        </div>
        """)

    return f"""
    <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4" id="item-grid-container">
        {''.join(item_html_parts)}
    </div>
    """


# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    It passes the initial state (credit and items) to the template,
    which then renders the complete initial UI.
    """
    # The context dictionary provides data to the Jinja2 template.
    context = {
        "request": request,
        "initial_credit": f"{credit:.2f}",
        "item_grid_html": _render_item_grid_html(credit),
        "retrieved_items": retrieved_items,
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)

@app.get("/item-info/{item_id}", response_class=HTMLResponse)
async def get_item_info(item_id: str):
    """
    Returns an HTML fragment with details for a specific item.
    This is triggered when a user clicks on an item in the grid.
    """
    item = ITEMS.get(item_id.upper())
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    html_content = f"""
    <div class="text-green-300">
        <p class="font-bold text-lg">{item_id.upper()}: {item.name}</p>
        <p class="text-sm">Calories: {item.calories}, Sodium: {item.sodium}mg</p>
    </div>
    """
    return HTMLResponse(content=html_content)

@app.post("/add-credit", response_class=HTMLResponse)
async def add_credit():
    """
    Adds $0.25 to the user's credit and returns two HTML fragments.
    One fragment updates the item grid (as items may become affordable),
    and an Out-Of-Band (OOB) fragment updates the credit display.
    """
    global credit
    credit += 0.25

    # Re-render the entire item grid to update button states (enabled/disabled).
    item_grid_html = _render_item_grid_html(credit)

    # Create the OOB fragment for the credit display.
    credit_display_html = f"""
    <div id="credit-display" hx-swap-oob="innerHTML" class="bg-gray-900 p-3 rounded-md text-2xl font-mono text-green-400 text-center">
        ${credit:.2f}
    </div>
    """

    # The final response combines the main target's HTML with the OOB swap HTML.
    return HTMLResponse(content=f"{item_grid_html}{credit_display_html}")

@app.post("/purchase/{item_id}", response_class=HTMLResponse)
async def purchase_item(item_id: str):
    """
    Handles an item purchase request.
    - If successful, it returns two OOB fragments to update the credit and retrieval bin.
    - If the item is sold out, it returns a 404 error with a specific message.
    """
    global credit
    item_id = item_id.upper()
    item = ITEMS.get(item_id)

    # Adhering to the contract: check for sold-out status first.
    if not item or item.stock <= 0:
        error_html = f"""
        <div class="text-red-500">
            <p class="font-bold text-xl">SOLD OUT</p>
            <p class="text-sm">Item {item_id} is unavailable.</p>
        </div>
        """
        # Return a 404 status code as specified in the contract.
        # HTMX can catch this and place the error content in a designated target.
        return HTMLResponse(content=error_html, status_code=404)

    # Although the UI should prevent this, a robust backend always validates.
    if credit < item.price:
        # This case is not in the contract, but it's good practice to handle.
        # We'll return an error message that can be displayed on the screen.
        error_html = f"""
        <div class="text-yellow-400">
            <p class="font-bold text-xl">INSUFFICIENT FUNDS</p>
            <p class="text-sm">Required: ${item.price:.2f}, You have: ${credit:.2f}</p>
        </div>
        """
        # A 402 Payment Required is a more semantic status code here.
        return HTMLResponse(content=error_html, status_code=402)

    # --- Transaction Logic ---
    credit -= item.price
    item.stock -= 1
    retrieved_items.append(item.name)

    # --- OOB Response Generation ---
    # As per the contract, we send back multiple OOB fragments.
    # The main response body is empty because all UI updates are OOB.
    credit_oob_html = f"""
    <div id="credit-display" hx-swap-oob="innerHTML" class="bg-gray-900 p-3 rounded-md text-2xl font-mono text-green-400 text-center">
        ${credit:.2f}
    </div>
    """
    retrieval_oob_html = f"""
    <div id="retrieval-bin-target" hx-swap-oob="beforeend">
        <div class="bg-yellow-500 p-4 rounded-lg shadow-inner text-yellow-900 font-bold animate-pulse">
            {item.name}
        </div>
    </div>
    """

    # Combine the fragments into a single response. The main body is empty.
    return HTMLResponse(content=f"{credit_oob_html}{retrieval_oob_html}")