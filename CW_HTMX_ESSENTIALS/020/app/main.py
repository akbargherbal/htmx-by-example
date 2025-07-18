# This file defines the core FastAPI application, its state, and API endpoints.
# As a Principal Engineer, my focus is on creating a clean, self-contained, and
# easily testable service that strictly adheres to the defined API contract.

from fastapi import FastAPI, Request, Response, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the central object that will
# manage all our API routes.
app = FastAPI()

# Configure Jinja2 for server-side HTML templating. This allows us to serve
# the initial UI and dynamic HTML fragments. The directory is specified relative
# to the project root.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# Per the project scope, we use a simple in-memory dictionary for our application
# state. This is not suitable for production but is ideal for this educational
# context to keep the focus on the API and HTMX interaction.
# We initialize the state with a default temperature.
_lab_state = {"temperature": 22}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial default.
    This utility is CRITICAL for ensuring test isolation, allowing each test
    to run against a clean, predictable state.
    """
    global _lab_state
    _lab_state = {"temperature": 22}


# --- Application Entrypoint (Serves index.html) ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the user's entry point to the
    application. It passes the initial state of the lab to the template,
    ensuring the UI is correctly rendered on first load.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_temperature": _lab_state["temperature"]}
    )


# --- API Endpoints ---

@app.post("/mix", response_class=HTMLResponse)
async def mix_chemicals(
    response: Response,
    chemical_a: str = Form(...),
    chemical_b: str = Form(...)
):
    """
    Handles the mixing of two chemicals submitted via a form.
    This endpoint demonstrates returning a standard HTML fragment and, conditionally,
    an `HX-Trigger` header to signal a secondary event on the client-side.
    """
    # The business logic: check for the specific combination that requires an alert.
    # This is a key part of the API contract.
    if chemical_a == "Acidic Reagent" and chemical_b == "Volatile Catalyst":
        # Using the `response.headers.append` method is the correct FastAPI
        # way to add custom headers required by the contract (e.g., for HTMX).
        response.headers["HX-Trigger"] = "VENT_NOW"

    # Construct the success message for the HTML fragment.
    result_description = f"{chemical_a} + {chemical_b}"
    html_content = f'<p class="text-green-400">[SUCCESS LOG] Mix complete: {result_description} formed.</p>'
    return HTMLResponse(content=html_content)


@app.post("/risky-mix", response_class=HTMLResponse)
async def perform_risky_mix(response: Response):
    """
    Simulates a failed experiment.
    This endpoint demonstrates returning a non-200 status code (422 Unprocessable
    Entity) to indicate a client error, as defined in the API contract. HTMX will
    handle this status code appropriately, often by swapping into an error target.
    """
    # We explicitly set the status code on the response object. This is more
    # declarative than using the `@app.post` decorator's `status_code` argument
    # when the status is the primary outcome of the logic.
    response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    html_content = '<p class="text-red-400">[ERROR LOG] Unprocessable Entity: Useless brown sludge formed. Experiment failed.</p>'
    return HTMLResponse(content=html_content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/temperature", response_class=HTMLResponse)
async def get_temperature():
    """
    Provides the current lab temperature.
    This endpoint is designed for polling, where a client (using hx-trigger="every 5s")
    repeatedly requests it to get the latest state and update a small part of the UI.
    """
    # The response is a simple HTML fragment containing only the data needed
    # for the target element, making the payload small and efficient.
    current_temp = _lab_state["temperature"]
    return HTMLResponse(content=f"{current_temp}°C")