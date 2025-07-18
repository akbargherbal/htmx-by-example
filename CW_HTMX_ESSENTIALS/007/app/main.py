# This file defines the main FastAPI application, its state, and its API endpoints.
# It's designed to be a self-contained, hyper-reliable backend for an HTMX-powered UI.

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

# --- Application Setup ---

# As a Principal Engineer, I advocate for clear separation of concerns.
# Here, we initialize the FastAPI application and configure the template engine.
# Pointing Jinja2 to the `app/templates` directory is a standard convention.
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# For this educational project, we use a simple in-memory list to store the state.
# This avoids database complexity and keeps the focus on the API/HTMX interaction.
# The state represents the list of items in the user's current order.
# A list of dictionaries is chosen for its direct compatibility with Jinja2 looping.
class OrderItem(BaseModel):
    name: str
    quantity: int

current_order: List[OrderItem] = []

def reset_state_for_testing():
    """
    This utility function is CRITICAL for test isolation.
    Pytest will call this before each test, ensuring that state from a previous
    test does not leak into the next, which is a common source of flaky tests.
    """
    global current_order
    current_order = []

# Initialize state on application startup.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is the user's entrypoint to the application. It renders the full
    UI, including the initial state of the order summary. The template will use
    the `order_items` context variable to display the (initially empty) order.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"order_items": current_order}
    )


# --- API Endpoints ---

@app.post("/add-item", response_class=HTMLResponse)
async def add_item(
    request: Request,
    item: str = Form(...),
    quantity: int = Form(...)
):
    """
    Handles adding an item to the current order.
    This endpoint embodies the core HTMX pattern: receive a request from the frontend,
    update the server's state, and return an HTML fragment representing the new UI state.

    FastAPI's `Form(...)` provides automatic data parsing and validation. If `quantity`
    is not a valid integer, FastAPI will return a 422 Unprocessable Entity response
    before our code even runs, which is a robust way to handle invalid input.
    """
    # Business logic: Check if the item already exists in the order.
    # Using a generator expression with `next` is an efficient way to find the
    # first matching item without iterating through the entire list unnecessarily.
    existing_item = next((order_item for order_item in current_order if order_item.name == item), None)

    if existing_item:
        # If the item exists, we update its quantity.
        existing_item.quantity += quantity
    else:
        # If it's a new item, we add it to the order list.
        current_order.append(OrderItem(name=item, quantity=quantity))

    # The key to this HTMX pattern: return an HTML fragment, not JSON.
    # We render a partial template containing only the updated order summary.
    # This fragment will be used by HTMX to swap the content of the `#order-summary` div.
    # We pass the *entire* updated order to the template so it can render the full list.
    return templates.TemplateResponse(
        request=request,
        name="partials/_order_summary.html",
        context={"order_items": current_order}
    )