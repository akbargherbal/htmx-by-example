# This file defines the main FastAPI application for the Community Garden.
# It handles all API logic, state management, and serves the initial HTML page.
# As a Principal Engineer, I've designed this to be simple, self-contained, and
# easily testable, which is ideal for this educational project.

import re
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# --- Application Setup ---

# The FastAPI instance is the core of our application.
app = FastAPI()

# Jinja2Templates is used to render our HTML. We point it to the 'app/templates'
# directory where index.html will be located.
templates = Jinja2Templates(directory="app/templates")


# --- State Management ---

# For this educational project, we use a simple in-memory dictionary for state.
# This avoids the complexity of a database, keeping the focus on HTMX and API interactions.
# The state is a dictionary representing the garden plots. Keys are plot IDs (int),
# and values are the names of the plants (str).
# We also track the next available plot ID to ensure uniqueness.
GARDEN_STATE = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to a predictable initial condition.
    This is a critical function for ensuring our tests are isolated and repeatable.
    It's called automatically by a pytest fixture before each test runs.
    """
    global GARDEN_STATE
    GARDEN_STATE = {
        "plots": {
            1: "Tomato",
            2: "Weed",
        },
        "next_plot_id": 3,
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Utility Functions ---

def normalize_for_testid(name: str) -> str:
    """
    Converts a plant name into a safe, consistent format for data-testid attributes.
    This is a good practice to ensure test selectors are predictable.
    Example: "Basil Plant" -> "basil-plant"
    """
    # Convert to lowercase
    s = name.lower()
    # Replace spaces and underscores with hyphens
    s = re.sub(r'[\s_]+', '-', s)
    # Remove any characters that are not alphanumeric or hyphens
    s = re.sub(r'[^a-z0-9-]', '', s)
    return s


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This is the entrypoint for the user. It renders the initial state of the garden
    using the Jinja2 template, passing the current plot data to be displayed.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"garden_plots": GARDEN_STATE["plots"]}
    )


# --- API Endpoints ---

@app.post("/garden/plots", response_class=HTMLResponse)
async def create_plant(plant_name: str = Form(...)):
    """
    Handles planting a new seed in an empty plot.
    It takes the plant name from the form submission, adds it to our in-memory state,
    and returns an HTML fragment representing the newly planted plot.
    """
    global GARDEN_STATE
    plot_id = GARDEN_STATE["next_plot_id"]
    GARDEN_STATE["plots"][plot_id] = plant_name
    GARDEN_STATE["next_plot_id"] += 1

    normalized_name = normalize_for_testid(plant_name)

    # This HTML fragment is returned directly to the client, where HTMX will
    # inject it into the DOM. This is the core mechanism of HTMX.
    return f"""
    <div id="plot-{plot_id}" data-testid="plant-plot-{normalized_name}" class="bg-gray-900 p-4 rounded-lg border border-gray-700 flex items-center justify-between">
      <span class="text-xl">🌱 {plant_name}</span>
      <div class="space-x-2">
        <button data-testid="replace-plant-button-{plot_id}" class="text-xs bg-yellow-600 text-white font-bold py-1 px-3 rounded hover:bg-yellow-700 transition-colors">Replace</button>
      </div>
    </div>
    """

@app.put("/garden/plots/{plot_id}", response_class=HTMLResponse)
async def replace_plant(plot_id: int):
    """
    Handles replacing an existing plant. As per the contract, this endpoint
    replaces the plant with a "Carrot". In a real application, the new plant
    name might come from the request body.
    """
    new_plant_name = "Carrot"
    GARDEN_STATE["plots"][plot_id] = new_plant_name
    normalized_name = normalize_for_testid(new_plant_name)

    # The response uses hx-swap-oob="true" (Out of Band swap) in the real HTML,
    # but the API contract only requires returning the fragment for the plot itself.
    # The `id` attribute on the returned div is crucial for HTMX to know where to swap the content.
    return f"""
    <div id="plot-{plot_id}" data-testid="plant-plot-{normalized_name}" class="bg-gray-900 p-4 rounded-lg border border-gray-700 flex items-center justify-between">
      <span class="text-xl">🥕 {new_plant_name}</span>
      <div class="space-x-2">
        <button data-testid="replace-plant-button-{plot_id}-after" class="text-xs bg-yellow-600 text-white font-bold py-1 px-3 rounded hover:bg-yellow-700 transition-colors">Replace</button>
      </div>
    </div>
    """

@app.delete("/garden/plots/{plot_id}", response_class=Response)
async def pull_weed(plot_id: int):
    """
    Handles removing a plant or weed from a plot.
    It removes the entry from our state dictionary. HTMX expects an empty 200 OK
    response to know the operation was successful, which will cause it to remove
    the element from the DOM.
    """
    if plot_id in GARDEN_STATE["plots"]:
        del GARDEN_STATE["plots"][plot_id]
    # Returning an empty Response with status 200 is the standard way to signal
    # to HTMX that the element that triggered the request should be removed.
    return Response(status_code=200)

@app.get("/garden/status", response_class=HTMLResponse)
async def get_garden_status():
    """
    Provides a status update on the garden. This is designed to be polled
    periodically by the frontend. The status changes based on whether there
s    are any weeds present in the plots.
    """
    if "Weed" in GARDEN_STATE["plots"].values():
        status_message = "Needs Weeding"
        status_emoji = "🚨"
        status_class = "bg-red-900/50"
        status_border_class = "border-red-700"
        status_text_class = "text-red-300"
    else:
        status_message = "Garden is Thriving"
        status_emoji = "✨"
        status_class = "bg-green-900/50"
        status_border_class = "border-green-700"
        status_text_class = "text-green-300"

    return f"""
    <div id="garden-status-after" data-testid="garden-status-after" class="mt-2 {status_class} p-4 rounded-lg border {status_border_class}">
      <p class="text-center {status_text_class}">{status_emoji} {status_message}</p>
    </div>
    """