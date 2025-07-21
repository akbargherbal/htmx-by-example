# This file defines the main FastAPI application, which serves as the backend
# for our HTMX-powered theater stage management system. It handles all API
# requests for changing set pieces, managing props, and triggering effects.

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# The FastAPI instance is the core of our application.
app = FastAPI()

# Jinja2Templates is used to render our main HTML page from a template file.
# This allows us to inject dynamic data into the initial page load.
templates = Jinja2Templates(directory="app/templates")


# --- State Management ---

# As per the project rules, we use a simple in-memory dictionary for our state.
# For this specific lesson, the state is not actively modified by the API endpoints,
# but we include the pattern for consistency and educational purposes.
# In a real application, this would be replaced by a database.
APP_STATE = {}


def reset_state_for_testing():
    """
    A mandatory utility function to reset the application's state. This is
    critical for ensuring that our automated tests run in an isolated environment,
    preventing results from one test from influencing another.
    """
    global APP_STATE
    APP_STATE = {}


# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the user's entry point to the
    application. It passes the initial application state to the template context.
    """
    # The context dictionary makes Python variables available inside the HTML template.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_state_variable": APP_STATE},  # Placeholder for future use
    )


# --- API Endpoints ---
# These endpoints correspond directly to the API Contract. Each one returns
# an HTML fragment that HTMX will use to update a part of the page.


@app.get("/set/backdrop-painting", response_class=HTMLResponse)
async def set_backdrop_painting():
    """
    Returns an HTML fragment for a stormy sea backdrop painting.
    This is intended to replace the content of the backdrop container.
    """
    return """
    <img src="https://placehold.co/200x150/333333/FFF?text=Stormy+Sea" alt="A stormy sea painting" class="w-full h-full object-cover">
    """


@app.get("/set/fireplace-prop", response_class=HTMLResponse)
async def set_fireplace_prop():
    """
    Returns an HTML fragment for a modern hearth prop.
    This is intended to replace the entire original fireplace element.
    """
    return """
    <div data-testid="fireplace-after" id="fireplace" class="prop bg-blue-900/50 p-4 rounded text-center border border-blue-700">
      <span class="text-2xl">💎</span>
      <p class="font-mono text-sm">Modern Hearth</p>
    </div>
    """


@app.get("/set/add-chair", response_class=HTMLResponse)
async def add_chair():
    """
    Returns an HTML fragment for a new chair prop.
    This is intended to be appended to the list of props on stage.
    """
    return """
    <div data-testid="chair-prop" class="prop bg-green-900/50 p-4 rounded text-center border border-green-700">
      <span class="text-2xl">🪑</span>
      <p class="font-mono text-sm">New Chair</p>
    </div>
    """


@app.get("/set/add-coat-rack", response_class=HTMLResponse)
async def add_coat_rack():
    """
    Returns an HTML fragment for a coat rack prop.
    This is intended to be inserted after the main stage container.
    """
    return """
    <div data-testid="coat-rack-prop" class="prop bg-purple-900/50 p-4 rounded text-center border border-purple-700 max-w-xs mx-auto mt-2">
      <span class="text-2xl">🧥</span>
      <p class="font-mono text-sm">Coat Rack</p>
    </div>
    """


@app.get("/props/inventory", response_class=HTMLResponse)
async def get_props_inventory():
    """
    Returns a larger HTML fragment representing the entire prop inventory.
    HTMX will use hx-select to pick out only the #antique-telephone element.
    """
    return """
    <!-- Full response from server -->
    <div id="inventory-list">
      <div id="fancy-vase" class="prop">
        <span>🏺</span>
        <p>Fancy Vase</p>
      </div>
      <div id="antique-telephone" class="prop p-4 rounded text-center border border-yellow-700 bg-yellow-900/50">
        <span class="text-2xl">☎️</span>
        <p class="font-mono text-sm">Antique Telephone</p>
      </div>
      <div id="grandfather-clock" class="prop">
        <span>🕰️</span>
        <p>Grandfather Clock</p>
      </div>
    </div>
    """


@app.post("/workshop/request", response_class=HTMLResponse)
async def request_workshop_item(
    stage_width: Annotated[int, Form()], stage_height: Annotated[int, Form()]
):
    """
    Handles a POST request from a form. It reads the 'stage_width' and
    'stage_height' values and includes them in the confirmation message.
    This demonstrates how HTMX can send data from form inputs.
    """
    # Using an f-string to dynamically create the response based on form data.
    return f"""
    <div data-testid="workshop-confirmation" class="w-full text-center p-2 bg-gray-700 rounded-md">
      <p class="text-lime-400">Confirmed: New set piece ordered for stage ({stage_width}x{stage_height}).</p>
    </div>
    """


@app.get("/cue/special-effects", response_class=HTMLResponse)
async def cue_special_effects():
    """
    Returns a simple confirmation message but, more importantly, sets a custom
    'HX-Trigger' header. This header tells HTMX to trigger client-side events
    (in this case, 'flash-lights' and 'play-sound').
    """
    # We must construct an HTMLResponse object directly to ensure our custom
    # headers are correctly attached to the final response.
    # Using the JSON object format and kebab-case for event names for max compatibility.
    content = "<p>Effects cued!</p>"
    headers = {"HX-Trigger": '{"flash-lights": null, "play-sound": null}'}
    return HTMLResponse(content=content, headers=headers)
