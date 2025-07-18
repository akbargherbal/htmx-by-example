# This file contains the core FastAPI application logic.
# It manages the application state in-memory and defines the API endpoints
# required by the contract. As a Principal Engineer, I emphasize clean separation
# of concerns; here, we separate HTML generation logic into helper functions
# to keep the endpoint handlers lean and readable.

from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# Instantiate the FastAPI application. This is the central object that will
# manage all our API routes.
app = FastAPI()

# Configure Jinja2Templates to look for templates in the 'app/templates' directory.
# This is standard practice for serving HTML files with FastAPI.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# As per the project scope, we use a simple Python dictionary for our state.
# This is not suitable for production but is perfect for this educational example
# as it avoids database complexity. Each key represents a smart home device.
device_state = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its default values.
    This is a critical function for ensuring test isolation. By calling this
    before each test, we guarantee that tests don't influence each other.
    """
    global device_state
    device_state = {
        "speaker": {"playlist": "90s Rock Anthems"},
        "light": {"is_on": True},
        "temperature": {"value": 22}
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- HTML Fragment Rendering Helpers ---
# These helpers encapsulate the logic for rendering a single device's HTML.
# This promotes code reuse and makes the API endpoints cleaner.

def _render_speaker_html(playlist_name: str) -> str:
    """Generates the HTML fragment for the speaker component."""
    return f"""
<div id="living-room-speaker" data-testid="living-room-speaker-after" class="bg-gray-900 p-4 rounded-lg flex items-center justify-between ring-2 ring-green-500">
    <div>
        <p class="font-bold text-lg">Living Room Speaker</p>
        <p class="text-gray-400">Playlist: <span class="font-mono text-green-300">{playlist_name}</span></p>
    </div>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-12c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z" /></svg>
</div>
    """.strip()

def _render_light_html(is_on: bool) -> str:
    """Generates the HTML fragment for the light component, with dynamic styling."""
    if is_on:
        ring_class = "ring-2 ring-yellow-400"
        status_text_color = "text-green-400"
        status_text = "On"
        icon_color = "text-yellow-400"
    else:
        ring_class = "ring-1 ring-gray-600"
        status_text_color = "text-red-400"
        status_text = "Off"
        icon_color = "text-gray-600"

    return f"""
<div id="kitchen-light" data-testid="kitchen-light-after" class="bg-gray-900 p-4 rounded-lg flex items-center justify-between {ring_class}">
    <div>
        <p class="font-bold text-lg">Kitchen Light</p>
        <p class="text-gray-400">Status: <span class="font-bold {status_text_color}">{status_text}</span></p>
    </div>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 {icon_color}" fill="currentColor" viewBox="0 0 20 20"><path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 14.95a1 1 0 001.414 1.414l.707-.707a1 1 0 00-1.414-1.414l-.707.707zM4 10a1 1 0 01-1 1H2a1 1 0 110-2h1a1 1 0 011 1zM10 18a1 1 0 011-1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.757 4.343a1 1 0 00-1.414 1.414l.707.707a1 1 0 001.414-1.414l-.707-.707zM10 5a1 1 0 011-1v-1a1 1 0 10-2 0v1a1 1 0 011-1zM5.05 5.05A1 1 0 006.465 3.636l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM10 16a6 6 0 110-12 6 6 0 010 12z"/></svg>
</div>
    """.strip()

def _render_temperature_html(temperature: int) -> str:
    """Generates the HTML fragment for the temperature component."""
    return f"""
<div id="ambient-temperature" data-testid="ambient-temperature-after" class="bg-gray-900 p-4 rounded-lg flex items-center justify-between ring-2 ring-cyan-500">
    <div>
        <p class="font-bold text-lg">Ambient Temperature</p>
        <p class="text-2xl font-mono text-cyan-300">{temperature}°C</p>
    </div>
    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" /></svg>
</div>
    """.strip()


# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. It passes the current device state
    to the template, allowing Jinja2 to render the initial UI.
    """
    # The context dictionary makes our Python state variables available inside the HTML template.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_state": device_state}
    )

@app.get("/all-status", response_class=HTMLResponse)
async def get_all_status():
    """
    Returns a combined HTML fragment representing the current state of all devices.
    This is used for a full refresh of the dashboard.
    """
    speaker_html = _render_speaker_html(device_state["speaker"]["playlist"])
    light_html = _render_light_html(device_state["light"]["is_on"])
    temp_html = _render_temperature_html(device_state["temperature"]["value"])
    
    # We combine the fragments into a single response body.
    # HTMX with an 'outerHTML' swap on a parent container can use this
    # to replace the entire block of devices at once.
    combined_html = f"{speaker_html}{light_html}{temp_html}"
    return Response(content=combined_html, media_type="text/html")

@app.post("/playlist", response_class=HTMLResponse)
async def set_playlist(playlistName: Annotated[str, Form()]):
    """
    Updates the speaker's playlist based on form data and returns the
    updated HTML fragment for the speaker component.
    """
    # Sanitize or validate input in a real application. Here we trust the input.
    device_state["speaker"]["playlist"] = playlistName
    
    # Return only the HTML for the component that changed. This is a core
    # principle of HTMX: sending "over the wire" only what is necessary.
    html_content = _render_speaker_html(playlistName)
    return Response(content=html_content, media_type="text/html")

@app.post("/toggle-light", response_class=HTMLResponse)
async def toggle_light():
    """
    Toggles the kitchen light's state (on/off) and returns the updated
    HTML fragment for the light component.
    """
    # This is a classic toggle pattern: flip the boolean state.
    current_state = device_state["light"]["is_on"]
    device_state["light"]["is_on"] = not current_state
    
    # Generate and return the new HTML based on the *new* state.
    html_content = _render_light_html(device_state["light"]["is_on"])
    return Response(content=html_content, media_type="text/html")

@app.get("/temperature", response_class=HTMLResponse)
async def get_temperature():
    """

    Returns the current HTML fragment for the temperature component.
    This could be used for a component that polls for updates periodically.
    """
    temp = device_state["temperature"]["value"]
    html_content = _render_temperature_html(temp)
    return Response(content=html_content, media_type="text/html")