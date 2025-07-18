# This file defines the main FastAPI application, which serves as the backend
# for our HTMX-driven educational project. As a Principal Engineer, my focus here
# is on creating clean, self-contained, and easily understandable endpoints that
# strictly adhere to the defined API contract.

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This 'app' object is the central point
# of the API, where all routes are registered.
app = FastAPI()

# Configure Jinja2 for server-side HTML templating. This allows us to render
# dynamic data into our HTML files. The directory is set to 'app/templates',
# which is a standard convention.
templates = Jinja2Templates(directory="app/templates")


# --- State Management ---

# Per the project's non-negotiable rules, all state is ephemeral and stored
# in a simple in-memory dictionary. This is purely for educational demonstration
# and would be replaced by a proper database in a production system.
# In this specific lesson, there is no dynamic state, so we use a placeholder.
initial_state = {"lesson": "htmx-oob-swap"}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its default.
    This is a critical function for ensuring test isolation, allowing each test
    to run against a clean, predictable state. It's called automatically by a
    pytest fixture before each test case.
    """
    global initial_state
    initial_state = {"lesson": "htmx-oob-swap"}


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the primary entrypoint for the user's
    browser. It passes the initial application state to the template, allowing
    the page to be rendered with dynamic data from the server.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_state": initial_state}
    )


# --- API Endpoints (Adhering to the API Contract) ---

# The following endpoints are designed to return small, specific HTML fragments.
# This is a core pattern in HTMX, where the server sends back just the HTML
# needed to update a portion of the page, rather than a full page reload or
# a JSON payload that requires client-side processing.

@app.get("/lego/pilot", response_class=HTMLResponse)
async def get_lego_pilot():
    """
    Returns an HTML fragment for a LEGO pilot.
    This demonstrates a simple content swap.
    """
    # The response is a raw HTML string. Using HTMLResponse ensures the
    # Content-Type header is correctly set to 'text/html'.
    return "<span>LEGO Pilot</span>"


@app.get("/lego/window-wall", response_class=HTMLResponse)
async def get_lego_window_wall():
    """
    Returns an HTML fragment for a wall section with a window.
    This is used to demonstrate swapping a more complex element.
    """
    # Using multiline strings for larger HTML fragments improves readability.
    # Note the 'id' and 'data-testid' attributes, which are crucial for HTMX
    # targeting and for stable testing.
    return """
    <div id="wall-section-1" data-testid="wall-section-1-final" class="w-40 h-20 bg-yellow-500 border-2 border-gray-900 flex items-center justify-center text-black font-semibold rounded-sm relative">
        Window Wall
        <div class="absolute w-10 h-10 bg-cyan-300 rounded border-2 border-gray-900"></div>
    </div>
    """


@app.get("/lego/top-brick", response_class=HTMLResponse)
async def get_lego_top_brick():
    """
    Returns an HTML fragment for a single red brick.
    This is used for demonstrating appending content.
    """
    return """
    <div class="w-10 h-10 bg-red-500 border-2 border-gray-900 flex items-center justify-center text-white text-xs font-semibold rounded-sm">Brick</div>
    """


@app.get("/lego/tree", response_class=HTMLResponse)
async def get_lego_tree():
    """
    Returns an HTML fragment for a LEGO tree.
    This demonstrates adding a multi-part element to the page.
    """
    return """
    <div data-testid="tree" class="flex flex-col items-center">
        <div class="w-16 h-20 bg-green-700 rounded-t-full border-2 border-gray-900"></div>
        <div class="w-6 h-10 bg-amber-800 border-2 border-gray-900"></div>
    </div>
    """


@app.get("/lego/castle-instructions", response_class=HTMLResponse)
async def get_castle_instructions():
    """
    Returns a full HTML document containing castle part definitions.
    This endpoint is specifically designed to demonstrate the 'hx-select'
    feature, where the client can extract a specific fragment from a larger
    document returned by the server.
    """
    # Note that this returns a complete HTML document, not just a fragment.
    # This simulates fetching a resource from which only a small part is needed.
    return """
    <html>
      <body>
        <h1>Full Castle Parts List</h1>
        <div id="castle-parts">
          <div id="tower-piece">... a tall tower ...</div>
          <div id="drawbridge-piece" data-testid="source-drawbridge">
            ... a wooden drawbridge ...
          </div>
          <div id="gate-piece">... a large gate ...</div>
        </div>
      </body>
    </html>
    """