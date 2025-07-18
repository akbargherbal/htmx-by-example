# This file defines the main FastAPI application, its state, and all API endpoints.
# As a Principal Engineer, I emphasize keeping the main application file clean and focused.
# It should clearly define the API contract implementation and state management.

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# The FastAPI instance is the core of our application.
app = FastAPI()

# Jinja2Templates is used to render our HTML. By convention, templates are stored
# in a 'templates' directory. For this educational project, it's in 'app/templates'.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# In a real-world application, this state would live in a database, cache (like Redis),
# or a dedicated state management service. For this educational project, a simple
# global dictionary suffices. It's crucial to encapsulate state access.
_APP_STATE = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This is a critical function for ensuring test isolation. Each test should start
    with a predictable, clean slate.
    """
    global _APP_STATE
    _APP_STATE = {
        "fuel_level": 98
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is the user's primary entry point to the application. It's responsible
    for rendering the initial UI with the current application state.
    """
    # The context dictionary passes server-side state to the Jinja2 template.
    # This is how we initially populate the UI with data.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_fuel_level": _APP_STATE["fuel_level"]}
    )


# --- API Endpoints (Implementing the Contract) ---

@app.get("/api/fuel-level", response_class=HTMLResponse)
async def get_fuel_level():
    """
    API endpoint to fetch the current fuel level.
    Returns an HTML fragment, designed to be swapped into the DOM by HTMX.
    """
    fuel = _APP_STATE["fuel_level"]
    # Using an f-string directly is acceptable for simple, trusted HTML fragments.
    # For more complex HTML, a dedicated template file is a better practice.
    return f'<p class="text-lg text-green-400 font-medium">Fuel: {fuel}%</p>'

@app.post("/api/calculate-route", response_class=HTMLResponse)
async def calculate_route(
    destination: Annotated[str, Form()],
    avoid_tolls: Annotated[str | None, Form()] = None
):
    """
    API endpoint to simulate calculating a route.
    It demonstrates handling POST requests with form data.
    """
    # The 'avoid_tolls' checkbox will have the value 'on' if checked, or None if not.
    # This logic creates a user-friendly message based on the form input.
    avoid_tolls_message = "avoiding tolls" if avoid_tolls == "on" else "via the fastest route"
    return f"""
    <p class="text-green-400">Route to '{destination}' {avoid_tolls_message} is being calculated...</p>
    """

@app.get("/api/tune-invalid-station", response_class=HTMLResponse)
async def tune_invalid_station():
    """
    Simulates an expected client error (404 Not Found).
    HTMX can handle non-200 responses, allowing for robust error handling on the frontend.
    We return a simple HTML message, which HTMX could display in an error container.
    """
    return HTMLResponse(content="<p>Error: Station not found.</p>", status_code=404)

@app.get("/api/check-gps-sensor", response_class=HTMLResponse)
async def check_gps_sensor():
    """
    Simulates an unexpected server error (500 Internal Server Error).
    This demonstrates how the backend can signal a critical failure to the frontend.
    """
    return HTMLResponse(content="<p>Error: GPS sensor is offline.</p>", status_code=500)

@app.get("/page/settings/race-mode", response_class=HTMLResponse)
async def access_race_mode():
    """
    Demonstrates a server-side redirect using the 'HX-Redirect' header.
    The response body is empty because the browser will be instructed to navigate
    to a new page entirely. The status code is 200, as the request itself was
    handled successfully.
    """
    return Response(content="", headers={"HX-Redirect": "/page/driving-mode-selection"})

@app.get("/page/driving-mode-selection", response_class=HTMLResponse)
async def get_driving_mode_selection_page():
    """
    This endpoint serves the target page for the HX-Redirect.
    It returns a full, standalone HTML document as specified in the API contract.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mode Selection</title>
        <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    </head>
    <body class="bg-gray-900 text-gray-300">
        <div class="container mx-auto p-8">
            <h1 class="text-4xl font-bold text-gray-100">Driving Mode Selection</h1>
            <p class="text-lg text-gray-400 mt-2">Please select a driving mode before accessing advanced settings.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)