# app/main.py

# This file defines the main FastAPI application, its state, and API endpoints.
# As a Principal Engineer, I emphasize keeping this file clean and focused on routing
# and request/response handling. Business logic should ideally be delegated to
# service modules, but for this small-scale educational app, it's acceptable here.

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 templates. This allows us to serve HTML files from a directory.
# It's crucial for the main application entrypoint (GET /).
templates = Jinja2Templates(directory="app/templates")


# --- State Management ---

# Per the project scope, we use a simple in-memory variable for state.
# For this specific lesson, no state is actually required by the API endpoints.
# However, we include the structure to maintain consistency with the project's
# architectural pattern.
# A real-world application would use a database, cache, or other persistent storage.
APP_STATE = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state.
    This is a critical function for ensuring test isolation. Each test should
    start with a clean, predictable state.
    """
    global APP_STATE
    APP_STATE = {}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This is the user's entrypoint to the web application. It provides the
    initial HTML structure that HTMX will interact with.
    The context dictionary is empty here as no initial dynamic data is needed for this lesson's UI.
    """
    return templates.TemplateResponse(
        request=request, name="index.html", context={"initial_state_variable": {}}
    )


# --- API Endpoints ---

@app.get("/renovation/item", response_class=HTMLResponse)
async def get_renovation_item():
    """
    Handles the GET request for a generic renovation item.
    This endpoint returns a simple, static HTML fragment as defined in the API contract.
    It demonstrates a basic HTMX swap.
    """
    # The HTML is returned directly as a string. Using HTMLResponse ensures the
    # Content-Type header is correctly set to 'text/html'.
    html_content = """<div data-testid="new-item-1" class="bg-cyan-900/50 text-cyan-300 p-6 rounded text-center">A shiny new glass pane</div>"""
    return HTMLResponse(content=html_content)

@app.get("/hardware-store/door-assembly", response_class=HTMLResponse)
async def get_door_assembly():
    """
    Handles the GET request for a full door assembly component.
    This endpoint is designed to be used with the `hx-select` attribute, where
    the client will only extract a portion of this larger HTML response.
    """
    # Note the multi-line string for readability. The key part is the span with id='doorknob'.
    html_content = """<!-- This is the full component from /hardware-store/door-assembly --><div class='door-component'>  <div class='door-panel wood-grain'>    A sturdy oak door panel.  </div>  <div class='door-hinges'>    Two iron hinges.  </div><span id='doorknob'>A brass doorknob</span> <!-- hx-select targets this ID -->  <div class='kick-plate'>    A metal kick plate.  </div></div>"""
    return HTMLResponse(content=html_content)

@app.post("/order/custom-cabinet", response_class=HTMLResponse)
async def order_custom_cabinet(width: str = Form(...)):
    """
    Handles the POST request to order a custom cabinet.
    This endpoint demonstrates handling form data (`hx-include`) and returning
    a dynamic HTML fragment based on that data.
    Using `Form(...)` makes 'width' a required form field. FastAPI handles the
    data extraction and validation.
    """
    # We use an f-string to dynamically insert the user-provided width into the
    # response HTML. This is a common pattern for creating responsive UI components.
    # In a real app, always sanitize user input to prevent XSS attacks.
    # For this educational context, we assume the input is safe.
    html_content = f"""<div data-testid="custom-cabinet" class="bg-orange-900/60 text-orange-300 p-6 rounded text-center" style="width: {width}; max-width: 100%;">Custom Cabinet (Width: {width})</div>"""
    return HTMLResponse(content=html_content)