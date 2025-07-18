# This file defines the main FastAPI application, its state, and API endpoints.
# As a Principal Engineer, I emphasize separating concerns. While state is in-memory
# for this educational project, in a real application, this would be handled by a
# dedicated service layer interacting with a database.

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 templates. This allows us to render HTML files from a directory.
# This is standard practice for serving web pages or complex HTML fragments.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# For this educational example, we use a simple in-memory dictionary to store our data.
# This avoids the complexity of a database, keeping the focus on the API and HTMX.
# The keys are 'slugs' that can be used in URLs.
EXHIBITS = {}

# This utility function resets the application's state. It's crucial for test isolation,
# ensuring that each test runs against a clean, predictable state.
def reset_state_for_testing():
    """Resets the in-memory state to its initial condition."""
    global EXHIBITS
    EXHIBITS = {
        "impressionism": {
            "name": "Impressionism",
            "description": "A 19th-century art movement characterized by relatively small, thin, yet visible brush strokes and an open composition."
        },
        "surrealism": {
            "name": "Surrealism",
            "description": "A cultural movement which developed in Europe in the aftermath of World War I and was largely influenced by Dada."
        },
        "cubism": {
            "name": "Cubism",
            "description": "An early-20th-century avant-garde art movement that revolutionized European painting and sculpture."
        }
    }

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This is the user's entrypoint to the application. It passes the initial
    state (the list of exhibits) to the template for rendering.
    """
    # The context dictionary is how we pass data from our Python backend
    # to the Jinja2 HTML template.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"exhibits": EXHIBITS}
    )


# --- API Endpoints ---

@app.get("/exhibit/{exhibit_slug}", response_class=HTMLResponse)
async def get_exhibit(exhibit_slug: str, request: Request):
    """
    Handles GET requests for a specific exhibit.
    This endpoint returns an HTML fragment, designed to be swapped into the
    main page by HTMX, updating only the relevant content area.
    """
    exhibit = EXHIBITS.get(exhibit_slug)
    if not exhibit:
        # In a real app, we'd return a proper 404 error fragment.
        # For this example, we assume valid slugs are always used.
        return HTMLResponse(content="<p>Exhibit not found.</p>", status_code=404)

    # We use an f-string to construct the HTML fragment. This is simple and effective
    # for small, controlled fragments. For more complex HTML, a dedicated
    # template file would be a better, more secure choice.
    html_content = f"""
    <h3 class="text-xl font-bold text-gray-100">Exhibit: {exhibit['name']}</h3>
    <p class="mt-2">{exhibit['description']} The browser URL would now be <code class="bg-gray-900 px-1 rounded">{request.url.path}</code>.</p>
    """
    return HTMLResponse(content=html_content)

@app.post("/request-from-archives", response_class=HTMLResponse)
async def request_from_archives():
    """
    Handles POST requests to fetch a piece from the archives.
    This simulates an action that retrieves data and returns an updated
    UI fragment, replacing the original button and status area.
    """
    # The data is hardcoded here for simplicity. In a real application, this
    # might involve a database query and state update.
    piece_name = "The Starry Night"
    artist_name = "Vincent van Gogh"

    html_content = f"""
    <div class="flex items-center space-x-4">
        <button data-testid="request-archive-btn" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-colors">Request Piece from Archives</button>
        <div data-testid="archive-content-area" class="bg-gray-700 border border-gray-600 rounded p-3">
            <p><span class="font-semibold text-gray-200">Retrieved:</span> '{piece_name}' by {artist_name}.</p>
        </div>
    </div>
    """
    return HTMLResponse(content=html_content)

@app.delete("/move-sculpture", response_class=HTMLResponse)
async def move_sculpture():
    """
    Handles DELETE requests to move a sculpture.
    This demonstrates using a different HTTP verb (DELETE) for a destructive
    or state-changing action. The response updates the UI to show the result
    and disables the button to prevent repeated actions.
    """
    # Again, hardcoded data for this educational example.
    sculpture_name = "The Thinker"
    new_location = "West Garden"

    html_content = f"""
    <div class="flex items-center justify-between">
        <div data-testid="sculpture-status" class="flex-grow p-3 rounded-md bg-green-900/50 border border-green-500/60">
            <p class="text-lg text-green-300"><span class="font-semibold text-green-200">Success! Sculpture:</span> '{sculpture_name}'</p>
            <p class="text-sm text-green-400">New Location: {new_location}</p>
        </div>
        <button data-testid="move-sculpture-btn" class="bg-gray-600 text-white font-bold py-2 px-4 rounded ml-4 opacity-50 cursor-not-allowed" disabled>Moved</button>
    </div>
    """
    return HTMLResponse(content=html_content)