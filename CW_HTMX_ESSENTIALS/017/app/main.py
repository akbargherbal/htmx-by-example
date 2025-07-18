# This file defines the main FastAPI application, including state management and API endpoints.
# As a Principal Engineer, I emphasize clean separation of concerns: state, routing, and business logic.

from fastapi import FastAPI, Request, Response, HTMLResponse
from fastapi.templating import Jinja2Templates
import itertools
from datetime import datetime

# --- Application Setup ---

# The FastAPI instance is the core of our application.
app = FastAPI()

# Jinja2Templates is used to render our HTML. This keeps our presentation logic
# separate from our application logic. The directory is specified relative to the project root.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---
# For this educational example, we use simple global variables for state.
# This is NOT suitable for production but is perfect for demonstrating HTMX concepts
# without the complexity of a database.

# A static list of headlines for the news ticker.
HEADLINES = [
    "Tech Giant Announces Breakthrough in AI.",
    "Global Markets Rally on Positive Economic News.",
    "New Study Reveals Surprising Health Benefits of Chocolate.",
    "Local Sports Team Wins Championship in Dramatic Finale.",
]

# The content for the main breaking news story.
BREAKING_STORY = "A sudden solar flare has caused temporary disruptions to satellite communications worldwide. Experts are monitoring the situation closely."

# The application's ephemeral state is stored in a single dictionary.
# This makes it easy to manage and reset for testing.
_state = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This function is CRITICAL for ensuring test isolation. By calling this
    before each test, we guarantee a clean, predictable environment,
    preventing tests from interfering with one another.
    """
    global _state
    # We use itertools.cycle to create an infinite iterator that loops over our headlines.
    # This is a memory-efficient way to handle cyclical data.
    _state["headline_cycler"] = itertools.cycle(HEADLINES)
    # The sidebar starts with one initial message. This list will be appended to.
    _state["sidebar_alerts"] = [
        f'<li class="text-gray-300"><span class="font-mono text-cyan-500">{datetime.now().strftime("%H:%M:%S")}</span> - System Initialized</li>'
    ]

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page for the application.
    It passes the initial state (the list of sidebar alerts) to the Jinja2 template.
    This ensures the UI is rendered correctly on the first page load.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"sidebar_alerts": _state["sidebar_alerts"]}
    )


# --- API Endpoints ---

@app.get("/api/headlines", response_class=HTMLResponse)
async def get_headlines():
    """
    Provides the next headline for the news ticker.
    Each request to this endpoint gets the next item from our cycling iterator.
    The response is a simple HTML fragment, as specified in the contract.
    """
    headline = next(_state["headline_cycler"])
    return HTMLResponse(content=f'<p class="text-sm">{headline}</p>')

@app.post("/api/broadcast/alert")
async def broadcast_alert():
    """
    Simulates broadcasting an alert to trigger other components.
    This endpoint is a key example of decoupling. It doesn't return any visible HTML.
    Instead, it returns an empty response with a special 'HX-Trigger' header.
    HTMX elements on the page can listen for this named event ('newBreakingNews')
    and fire their own requests, allowing for complex, event-driven interactions.
    """
    return Response(status_code=200, headers={"HX-Trigger": "newBreakingNews"})

@app.get("/api/story/breaking", response_class=HTMLResponse)
async def get_breaking_story():
    """
    Returns the HTML fragment for the main breaking news story.
    This endpoint is designed to be called by an element that was triggered by the
    'newBreakingNews' event from the /api/broadcast/alert endpoint.
    """
    html_content = f"""
    <h3 class="text-xl font-bold text-red-500">BREAKING NEWS</h3>
    <p class="mt-2 text-gray-300">{BREAKING_STORY}</p>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/broadcast/coordinated-update", response_class=HTMLResponse)
async def broadcast_coordinated_update():
    """
    Demonstrates a coordinated update using an Out-of-Band (OOB) swap.
    A single API response updates two separate areas of the page.

    1.  The main content (the breaking news story) is returned normally.
    2.  An additional HTML fragment for the sidebar is marked with `hx-swap-oob="true"`.
        HTMX finds this fragment, looks for an element with a matching ID (`alerts-sidebar-list`),
        and replaces it. This is a powerful technique for efficient UI updates.
    """
    # First, update the server's state by adding the new alert.
    timestamp = datetime.now().strftime("%H:%M:%S")
    new_alert_html = f'<li class="text-gray-300"><span class="font-mono text-cyan-400">{timestamp}</span> - Coordinated Update Received</li>'
    _state["sidebar_alerts"].append(new_alert_html)

    # The main fragment to be swapped into the default target.
    main_fragment = f"""
    <h3 class="text-xl font-bold text-red-500">BREAKING NEWS</h3>
    <p class="mt-2 text-gray-300">{BREAKING_STORY}</p>
    """

    # The OOB fragment that will replace the entire sidebar list.
    # We rebuild the full list from our updated state.
    all_alerts_html = "".join(_state["sidebar_alerts"])
    oob_fragment = f"""
    <ul id="alerts-sidebar-list" hx-swap-oob="true" class="list-disc list-inside space-y-2 text-sm">
        {all_alerts_html}
    </ul>
    """

    # Combine both fragments into a single response body. HTMX will parse it.
    return HTMLResponse(content=main_fragment + oob_fragment)