# This file defines the main FastAPI application, its endpoints, and state management.
# As a Principal Engineer, I emphasize clear separation of concerns. Here, we define
# data (HTML fragments) separately from the routing logic for maintainability.

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 for server-side HTML rendering. The 'app/templates' directory
# is the standard location for web templates.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory Data & State Management ---

# For this educational project, we define the HTML fragments directly in code.
# In a real-world application, these would likely be generated from a database
# and rendered through more complex templates, but this approach is perfect
# for isolating the HTMX-specific backend logic we want to demonstrate.
T_SHIRTS_HTML = """<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
  <!-- Product Card 1 -->
  <div class="bg-gray-700 p-4 rounded-lg shadow">
    <h4 class="text-xl font-bold text-gray-100">HTMX Logo Tee</h4>
    <p class="text-gray-400 mt-1">$28.00</p>
  </div>
  <!-- Product Card 2 -->
  <div class="bg-gray-700 p-4 rounded-lg shadow">
    <h4 class="text-xl font-bold text-gray-100">"I Use Arch" Tee</h4>
    <p class="text-gray-400 mt-1">$32.00</p>
  </div>
</div>"""

HATS_HTML = """<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
  <!-- Product Card 1 -->
  <div class="bg-gray-700 p-4 rounded-lg shadow">
    <h4 class="text-xl font-bold text-gray-100">Classic Snapback</h4>
    <p class="text-gray-400 mt-1">$25.00</p>
  </div>
  <!-- Product Card 2 -->
  <div class="bg-gray-700 p-4 rounded-lg shadow">
    <h4 class="text-xl font-bold text-gray-100">Winter Beanie</h4>
    <p class="text-gray-400 mt-1">$22.00</p>
  </div>
</div>"""

CHECKOUT_SUCCESS_HTML = """<p class="text-green-400 font-semibold">✓ Order placed successfully!</p>"""

# Per project rules, we must have an in-memory state and a reset function.
# Even though our API endpoints are stateless, this pattern is critical for
# building testable applications that do have state. It ensures that
# tests run in a clean, predictable environment.
app_state = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state. This is a critical function
    for ensuring that our automated tests are isolated and repeatable.
    """
    global app_state
    app_state = {}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the entrypoint for the user's
    browser. It passes the initial state (the default T-shirt product list)
    to the template, so the page is fully rendered on first load.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"products_html": T_SHIRTS_HTML}
    )

@app.get("/products/t-shirts", response_class=HTMLResponse)
async def get_t_shirts():
    """
    API endpoint to fetch the T-Shirts HTML fragment.
    This is designed to be called by an HTMX request to swap content.
    Using `Response` directly gives us fine-grained control over the media type.
    """
    return Response(content=T_SHIRTS_HTML, media_type="text/html; charset=utf-8")

@app.get("/products/hats", response_class=HTMLResponse)
async def get_hats():
    """
    API endpoint to fetch the Hats HTML fragment.
    Like the T-shirt endpoint, this serves a partial HTML response for HTMX.
    """
    return Response(content=HATS_HTML, media_type="text/html; charset=utf-8")

@app.post("/checkout/process", response_class=HTMLResponse)
async def process_checkout():
    """
    API endpoint to simulate processing a checkout.
    In a real app, this would involve database writes and payment processing.
    Here, it simply returns a success message fragment for HTMX to display.
    """
    return Response(content=CHECKOUT_SUCCESS_HTML, media_type="text/html; charset=utf-8")