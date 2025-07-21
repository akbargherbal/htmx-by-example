# This file defines the main FastAPI application for the "Personal Chef & Smart Kitchen" demo.
# As a Principal Engineer, my focus is on creating a clear, reliable, and easily testable API
# that strictly adheres to the defined contract.

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our web service.
app = FastAPI()

# Configure Jinja2 templates. This allows us to render HTML files from a directory,
# separating our presentation logic from our application logic.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# PRINCIPLE: For this educational project, we avoid databases and external dependencies.
# State is managed in a simple global variable. This is NOT suitable for production
# but is perfect for demonstrating the core HTMX concepts in an isolated way.
CHEF_STATUS_INITIAL = "Ready and waiting..."
chef_status = CHEF_STATUS_INITIAL


def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This is a critical utility for ensuring that our automated tests run in a
    predictable and isolated environment, preventing one test from affecting another.
    """
    global chef_status
    chef_status = CHEF_STATUS_INITIAL


# --- Application Entrypoint (Serves the main HTML page) ---


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is the user's entrypoint to the application. It provides the
    full HTML document, including the initial state of the application, which
    the frontend will then modify with HTMX requests.
    """
    # The context dictionary passes server-side data to the Jinja2 template.
    # Here, we pass the initial chef_status so the page loads with the correct data.
    return templates.TemplateResponse(
        request=request, name="index.html", context={"chef_status": chef_status}
    )


# --- API Endpoints (Implement the API Contract) ---


@app.get("/api/kitchen/water", response_class=HTMLResponse)
async def get_water():
    """
    Handles the GET request for a glass of water.
    This is a simple, idempotent GET endpoint that always returns the same
    static HTML fragment, as defined in the API contract.
    """
    # [RE-SKIN] Updated HTML fragment to match the new slate/teal theme and font sizes.
    html_content = """
<div class="text-center bg-slate-700/50 p-4 rounded-lg text-base md:text-lg">
  <p class="text-3xl">💧</p>
  <p class="text-slate-300 font-medium">Here is your glass of water.</p>
</div>
"""
    return HTMLResponse(content=html_content)


@app.post("/api/kitchen/recipes", response_class=HTMLResponse)
async def add_recipe(recipeName: str = Form(...)):
    """
    Handles the POST request to add a new recipe.
    This endpoint demonstrates handling form data (`application/x-www-form-urlencoded`).
    The `Form(...)` dependency tells FastAPI to extract the 'recipeName' field
    from the request body. The response dynamically includes this name.
    """
    # [RE-SKIN] Updated HTML fragment to match the new slate/teal theme and font sizes.
    html_content = f"""
<div class="text-center bg-slate-700/50 p-4 rounded-lg text-base md:text-lg">
  <p class="text-3xl">📖</p>
  <p class="text-slate-300 font-medium">Recipe for "{recipeName}" added to the cookbook!</p>
</div>
"""
    return HTMLResponse(content=html_content)


@app.put("/api/kitchen/soup", response_class=HTMLResponse)
async def adjust_soup_seasoning():
    """
    Handles the PUT request to adjust the soup's seasoning.
    PUT is the correct HTTP verb here as we are modifying/updating the state
    of a resource (the soup). In this demo, it simply returns a confirmation.
    """
    # [RE-SKIN] Updated HTML fragment to match the new slate/teal theme and font sizes.
    html_content = """
<div class="text-center bg-slate-700 p-4 rounded-lg text-base md:text-lg">
  <p class="text-3xl">🍲</p>
  <p class="text-slate-300 font-medium">The soup has been perfectly seasoned.</p>
</div>
"""
    return HTMLResponse(content=html_content)


@app.delete("/api/kitchen/toast")
async def discard_toast():
    """
    Handles the DELETE request to discard the toast.
    DELETE is the appropriate verb for removing a resource. The API contract
    specifies no response body for this action, which is a common pattern for
    DELETE requests. HTMX can be configured to swap nothing on a 200 OK.
    We return a `Response` with a 200 status code and empty content.
    """
    return Response(content="", status_code=200)


@app.get("/api/kitchen/chef-status", response_class=HTMLResponse)
async def get_chef_status():
    """
    Handles the GET request for the chef's current status.
    This endpoint is designed for polling. The frontend will call it repeatedly
    to get the latest status, which is then swapped into the UI.
    """
    # The response dynamically includes the current value of our in-memory state.
    html_content = f"""
<p><strong>Chef's Status:</strong> {chef_status}</p>
"""
    return HTMLResponse(content=html_content)
