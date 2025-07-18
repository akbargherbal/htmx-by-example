# This file defines the main FastAPI application, including all API endpoints
# and in-memory state management for an educational flight departures board.
# As a Principal Engineer, I'm ensuring the code is clean, well-commented,
# and strictly follows the defined API contract.

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 for server-side HTML rendering. The 'app/templates' directory
# is the standard location for these files. This is used for serving the main
# page and any other full HTML pages.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# In a real-world application, this data would live in a database.
# For this educational project, we use a simple in-memory dictionary to store
# the state of our flights. This makes the example self-contained and easy to run.
# This constant defines the pristine, default state of the flights.
FLIGHTS_DATA_DEFAULT = {
    "FL123": {
        "id": "FL123",
        "destination": "New York (JFK)",
        "gate": "A2 (Gate Change)",
        "status": "Boarding",
        "status_color": "blue",
        "airline": "American Airlines",
        "aircraft": "Boeing 777"
    },
    "BA456": {
        "id": "BA456",
        "destination": "London (LHR)",
        "gate": "B3",
        "status": "On Time",
        "status_color": "green",
        "airline": "British Airways",
        "aircraft": "Airbus A380"
    },
    "AF789": {
        "id": "AF789",
        "destination": "Paris (CDG)",
        "gate": "C5",
        "status": "Delayed",
        "status_color": "yellow",
        "airline": "Air France",
        "aircraft": "Boeing 787"
    }
}

# This variable will hold the current state of the application.
# It's initialized as an empty dict and populated by the reset function.
flights_state = {}

def reset_state_for_testing():
    """
    Resets the in-memory state to its default. This is a critical function
    for ensuring that our automated tests run in an isolated, predictable environment.
    Each test should start with the same clean slate.
    """
    global flights_state
    # We use deepcopy to ensure the original constant is never modified.
    import copy
    flights_state = copy.deepcopy(FLIGHTS_DATA_DEFAULT)

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the user's entrypoint to the
    application. It passes the initial, complete state of all flights to the
    template, which then renders the full UI.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"flights": list(flights_state.values())}
    )


# --- API Endpoints ---

@app.get("/api/flights", response_class=HTMLResponse)
async def get_flights():
    """
    API endpoint to fetch the current list of flights as an HTML fragment.
    This is designed to be called via HTMX polling (hx-get) to update the
    departures table body (tbody) without a full page reload.
    """
    # We construct the HTML fragment directly. For a small, specific fragment like this,
    # an f-string is often simpler and more performant than a full template render.
    html_rows = ""
    for flight in flights_state.values():
        html_rows += f"""
        <tr class="hover:bg-gray-700/50 cursor-pointer" hx-boost="true" hx-target="#flight-details-content">
          <td class="p-3" data-testid="flight-row-link-{flight['id']}-updated"><a href="/flights/{flight['id']}">{flight['id']}</a></td>
          <td class="p-3">{flight['destination']}</td>
          <td class="p-3 font-bold text-orange-400">{flight['gate']}</td>
          <td class="p-3"><span class="p-1.5 text-xs font-medium uppercase tracking-wider text-{flight['status_color']}-300 bg-{flight['status_color']}-800/50 rounded-lg">{flight['status']}</span></td>
        </tr>
        """
    return HTMLResponse(content=html_rows)


@app.post("/api/announce-gate-change")
async def announce_gate_change():
    """
    API endpoint that simulates an urgent, out-of-band server event.
    It returns no content but includes a special HTMX header, 'HX-Trigger'.
    This tells the frontend to trigger a custom event named 'urgentUpdate',
    which can be listened for to perform actions like showing an alert.
    """
    # The key here is the header, not the body. We return a Response object
    # to have full control over the headers. The status code is 200 OK.
    return Response(content="", status_code=200, headers={"HX-Trigger": "urgentUpdate"})


@app.post("/api/scan-pass")
async def scan_pass(ticket_type: Annotated[str, Form()]):
    """
    API endpoint that simulates scanning a boarding pass. Based on the form data,
    it can trigger a client-side redirect using the 'HX-Redirect' header.
    This is a powerful HTMX pattern for navigation without a full page load.
    """
    # This endpoint demonstrates a server-directed redirect.
    # If the ticket is 'Standard', we instruct the client to navigate to '/access-denied'.
    if ticket_type == "Standard":
        return Response(content="", status_code=200, headers={"HX-Redirect": "/access-denied"})
    # In a real app, other ticket types would be handled here.
    return Response(content="Access Granted", status_code=200)


@app.get("/flights/{flight_id}", response_class=HTMLResponse)
async def get_flight_details(flight_id: str):
    """
    API endpoint to get the detailed information for a single flight.
    This is used by hx-boost on the flight rows. It returns an HTML fragment
    that replaces the content of the '#flight-details-content' div.
    """
    flight = flights_state.get(flight_id)
    if not flight:
        return HTMLResponse(content="<p>Flight not found.</p>", status_code=404)

    # Constructing the detail view fragment.
    html_content = f"""
    <div id="flight-details-content" class="bg-gray-900/50 p-4 rounded-lg border border-gray-700 space-y-3">
      <h4 class="text-xl font-bold text-white">Flight {flight['id']} Details</h4>
      <div class="text-gray-400">
        <p><span class="font-semibold text-gray-300">Destination:</span> {flight['destination']}</p>
        <p><span class="font-semibold text-gray-300">Airline:</span> {flight['airline']}</p>
        <p><span class="font-semibold text-gray-300">Aircraft:</span> {flight['aircraft']}</p>
        <p><span class="font-semibold text-gray-300">Status:</span> <span class="text-{flight['status_color']}-400">{flight['status']}</span></p>
        <p><span class="font-semibold text-gray-300">Gate:</span> <span class="text-orange-400">{flight['gate']}</span></p>
      </div>
    </div>
    """
    return HTMLResponse(content=html_content)


@app.get("/access-denied", response_class=HTMLResponse)
async def get_access_denied_page():
    """
    Serves a full, static HTML page for the 'Access Denied' screen.
    This is the destination for the HX-Redirect from the /api/scan-pass endpoint.
    """
    # Since this is a full, static page, we return it as a complete HTML document.
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Access Denied</title>
      <script src="https://cdn.tailwindcss.com/3.4.1"></script>
    </head>
    <body class="bg-gray-900 text-gray-300 font-sans">
      <div class="container mx-auto p-4 sm:p-6 lg:p-8">
        <div class="bg-red-900/50 border border-red-700 rounded-lg p-8 text-center">
          <h1 class="text-5xl font-extrabold text-red-500">ACCESS DENIED</h1>
          <p class="mt-4 text-lg text-red-300">Standard tickets do not grant access to this area. You have been redirected.</p>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)