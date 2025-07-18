# This file defines the main FastAPI application, including state management and API endpoints.
# It is designed as a self-contained, in-memory application for educational purposes,
# demonstrating how to build a backend for HTMX-driven frontends without a database.

import re
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Principal Engineer's Note:
# Instantiating the FastAPI app. This is the core of our web service.
app = FastAPI()

# Setting up Jinja2 templates. This allows us to render HTML fragments dynamically.
# The backend will return these fragments in response to HTMX requests.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# Principal Engineer's Note:
# For this educational project, we manage state using simple global variables.
# This is NOT suitable for production but is perfect for demonstrating core concepts
# without the complexity of a database.
# We use a dictionary for the inventory for O(1) lookups and deletions by ID.
# The state is defined by the inventory, the currently equipped item, and a counter for new item IDs.

# We define the initial state separately so we can easily reset to it for testing.
INITIAL_INVENTORY: Dict[int, Dict[str, str]] = {
    1: {"name": "Wooden Sword", "slug": "wooden-sword"},
    2: {"name": "Herbs", "slug": "herbs"},
}
INITIAL_EQUIPPED_ITEM_ID: Optional[int] = None
INITIAL_NEXT_ITEM_ID: int = 3

# These global variables will hold the current state of the application.
_inventory: Dict[int, Dict[str, str]] = {}
_equipped_item_id: Optional[int] = None
_next_item_id: int = 0


def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This is a critical function for ensuring test isolation. It's called
    automatically by a pytest fixture before each test runs.
    """
    global _inventory, _equipped_item_id, _next_item_id
    # We use .copy() to prevent mutations of the initial state constants.
    _inventory = INITIAL_INVENTORY.copy()
    _equipped_item_id = INITIAL_EQUIPPED_ITEM_ID
    _next_item_id = INITIAL_NEXT_ITEM_ID


# Initialize the state when the application starts.
reset_state_for_testing()


# --- Utility Functions ---

def slugify(text: str) -> str:
    """
    A simple utility function to convert a string into a URL-friendly "slug".
    This ensures consistency for `data-testid` attributes.
    Example: "Health Potion" -> "health-potion"
    """
    text = text.lower()
    # Remove characters that are not alphanumeric, spaces, or hyphens.
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace spaces and repeated hyphens with a single hyphen.
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is responsible for the initial page load. It passes the complete
    application state to the main template, which then renders the initial UI.
    """
    equipped_item = _inventory.get(_equipped_item_id) if _equipped_item_id else None
    context = {
        "inventory": _inventory,
        "equipped_item": equipped_item,
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)


# --- API Endpoints ---

@app.get("/inventory", response_class=HTMLResponse)
async def get_inventory(request: Request):
    """
    Returns the complete inventory list as an HTML fragment.
    This is used for refreshing the inventory display.
    """
    return templates.TemplateResponse(
        request=request,
        name="_inventory_list.html",
        context={"inventory": _inventory}
    )


@app.post("/inventory", response_class=HTMLResponse)
async def create_item(request: Request, itemName: str = Form(...)):
    """
    Creates a new item in the inventory from form data.
    It adds the item to the in-memory state and returns the updated
    inventory list, highlighting the newly created item.
    """
    global _next_item_id
    new_id = _next_item_id
    _inventory[new_id] = {"name": itemName, "slug": slugify(itemName)}
    _next_item_id += 1

    # We pass the new_item_id to the template so it can apply special styling.
    return templates.TemplateResponse(
        request=request,
        name="_inventory_list.html",
        context={"inventory": _inventory, "new_item_id": new_id}
    )


@app.put("/inventory/equip/{item_id}", response_class=HTMLResponse)
async def equip_item(request: Request, item_id: int):
    """
    Equips an item specified by its ID.
    It updates the in-memory state and returns an HTML fragment for the
    'equipped item' slot, which HTMX will swap into the page.
    """
    global _equipped_item_id
    if item_id in _inventory:
        _equipped_item_id = item_id
        equipped_item = _inventory[item_id]
        return templates.TemplateResponse(
            request=request,
            name="_equipped_item.html",
            context={"equipped_item": equipped_item}
        )
    # In a real app, you'd handle the "not found" case more gracefully.
    return Response(status_code=404, content="Item not found")


@app.delete("/inventory/item/{item_id}", response_class=HTMLResponse)
async def drop_item(request: Request, item_id: int):
    """
    Deletes an item from the inventory.
    It removes the item from the in-memory state and returns the updated
    inventory list HTML fragment.
    """
    global _equipped_item_id
    if item_id in _inventory:
        del _inventory[item_id]
        # If the dropped item was the one equipped, un-equip it.
        if _equipped_item_id == item_id:
            _equipped_item_id = None
        return templates.TemplateResponse(
            request=request,
            name="_inventory_list.html",
            context={"inventory": _inventory}
        )
    # In a real app, you'd handle the "not found" case more gracefully.
    return Response(status_code=404, content="Item not found")


@app.get("/treasure-chest", response_class=HTMLResponse)
async def get_treasure_chest(request: Request):
    """
    Returns a container with multiple lootable items.
    The frontend uses hx-select to pick one item from this response
    and append it to the inventory. This demonstrates how a single API
    response can be used for multiple UI updates.
    """
    return templates.TemplateResponse(
        request=request,
        name="_treasure_chest.html",
        context={}
    )