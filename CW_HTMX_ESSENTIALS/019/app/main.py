# This file defines the main FastAPI application, its state, and API endpoints.
# As a Principal Engineer, I emphasize clean separation of concerns. Here, we manage
# state, define routes, and handle business logic in a single, focused module.
# This is suitable for a small, educational application. In a larger system,
# we would separate these into different modules (e.g., `state.py`, `routers/`).

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 templates. This allows us to render HTML files from a directory.
# The 'app/templates' directory is the conventional place for these files.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# PRINCIPAL ENGINEER'S NOTE on State:
# For this educational project, we are explicitly avoiding a database.
# All state is stored in simple Python dictionaries. This is ephemeral and will
# reset every time the application restarts. This approach is great for demos
# but is NOT suitable for production environments where data persistence is required.

# Static data representing the available songs in the jukebox.
# In a real application, this would come from a database.
SONGS = {
    "B5": {"name": "Hound Dog", "runtime": "2:16"},
    "C1": {"name": "Jailhouse Rock", "runtime": "2:35"},
    "A3": {"name": "Johnny B. Goode", "runtime": "2:41"},
}

# The dynamic state of the application. It tracks whether the jukebox is
# enabled (i.e., a coin has been inserted) and the current song queue.
# We initialize it in a disabled state with an empty queue.
jukebox_state = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This is a critical utility for ensuring that our automated tests run in an
    isolated environment, free from the side effects of previous tests.
    """
    global jukebox_state
    jukebox_state = {
        "enabled": False,
        "queue": [] # A list of song IDs, e.g., ["C1", "A3"]
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is the primary entry point for a user visiting the application.
    It passes the complete initial state (songs and jukebox status) to the
    Jinja2 template, which then renders the UI accordingly.
    """
    # The context dictionary is what makes the data available inside the HTML template.
    # For example, in Jinja, you can access `jukebox_state.enabled`.
    context = {
        "songs": SONGS,
        "jukebox_state": jukebox_state,
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)


# --- API Endpoints ---

@app.post("/enable-jukebox", response_class=HTMLResponse)
async def enable_jukebox():
    """
    Handles the "coin insertion" by enabling the jukebox.
    This endpoint modifies the application state and returns an HTML fragment
    containing the newly enabled song selection controls.
    """
    # State mutation: The core logic of this endpoint.
    jukebox_state["enabled"] = True

    # Construct the HTML response based on the API contract.
    # We iterate through our static song data to build the list of selectors.
    # This ensures the UI is always in sync with the backend data.
    html_content = '<div data-testid="song-selectors-enabled" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">'
    for song_id, song_details in SONGS.items():
        html_content += f"""
        <div class="bg-gray-700 p-4 rounded-lg flex flex-col justify-between">
            <p class="font-bold text-lg text-gray-100">{song_id} - {song_details['name']}</p>
            <div class="flex items-center space-x-2 mt-4">
                <button
                    data-testid="song-{song_id}-preview-enabled"
                    hx-get="/songs/preview?songId={song_id}"
                    hx-target="#main-display"
                    class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors">
                    Preview
                </button>
                <button
                    data-testid="song-{song_id}-select-enabled"
                    hx-post="/songs/queue"
                    hx-vals='{{"songId": "{song_id}"}}'
                    hx-target="#song-queue-list"
                    hx-swap="beforeend"
                    class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors">
                    Select
                </button>
            </div>
        </div>
        """
    html_content += '</div>'

    return HTMLResponse(content=html_content)

@app.get("/songs/preview", response_class=HTMLResponse)
async def preview_song(songId: str):
    """
    Provides a preview of a selected song.
    It looks up the song by its ID and returns an HTML fragment with its details.
    This demonstrates a read-only operation that doesn't change state.
    """
    song = SONGS.get(songId)
    if not song:
        # Defensive programming: always handle cases where the requested data doesn't exist.
        raise HTTPException(status_code=404, detail="Song not found")

    # The response is a simple HTML fragment, as specified in the contract.
    html_content = f"""
    <div data-testid="main-display-after-preview" class="text-center text-green-400 py-4">
        <p class="text-xl font-mono">Song: {song['name']}</p>
        <p class="text-lg font-mono">Runtime: {song['runtime']}</p>
    </div>
    """
    return HTMLResponse(content=html_content)

@app.post("/songs/queue", response_class=HTMLResponse)
async def queue_song(songId: Annotated[str, Form()]):
    """
    Adds a song to the queue.
    This endpoint receives the songId from a form post, updates the queue state,
    and returns an HTML fragment for the new list item to be appended to the UI.
    """
    song = SONGS.get(songId)
    if not song:
        # Ensure the song exists before adding it to the queue.
        raise HTTPException(status_code=404, detail="Song not found")

    # State mutation: add the selected song to the queue.
    jukebox_state["queue"].append(songId)

    # The response is a single list item, designed to be swapped into the DOM.
    # The `data-testid` is crucial for reliable end-to-end testing.
    html_content = f"""
    <li data-testid="queue-item-{songId}">
        {songId} - {song['name']}
    </li>
    """
    return HTMLResponse(content=html_content)