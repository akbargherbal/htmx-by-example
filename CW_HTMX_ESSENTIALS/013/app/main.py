# This file defines the main FastAPI application, its endpoints, and state management.
# As a Principal Engineer, I emphasize clean separation of concerns, but for this
# educational example, all logic is contained in this single file as per the requirements.

from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any

# --- Application Setup ---

# Instantiate the FastAPI application. This is the core of our API.
app = FastAPI()

# Configure Jinja2 templates. This allows us to render HTML files from a directory.
# The 'app/templates' directory is the standard location for a project of this structure.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# Per the project scope, we use a simple in-memory dictionary for our application state.
# This is NOT suitable for production but is perfect for this self-contained educational module.
# We'll store the last submitted order here to demonstrate passing state to the root template.
app_state: Dict[str, Any] = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state.
    This is a critical function for ensuring test isolation. By calling this
    before each test, we guarantee that one test cannot influence another.
    """
    global app_state
    app_state = {"last_order": None}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page.
    This endpoint is the user's entrypoint to the application. It renders the
    main HTML shell and passes the current application state to the template.
    """
    # The context dictionary makes Python variables available inside the Jinja2 template.
    # Here, we pass the 'last_order' so the initial page can render it if it exists.
    return templates.TemplateResponse(
        request=request, name="index.html", context={"last_order": app_state["last_order"]}
    )


# --- API Endpoints ---

@app.get("/menu-item", response_class=HTMLResponse)
async def get_menu_item(name: str):
    """
    Handles GET requests for predefined menu items like 'soup' or 'special'.
    This endpoint returns a specific HTML fragment based on the 'name' query parameter.
    This is a common pattern in HTMX where a user action fetches a piece of UI to display.
    """
    # We use a simple conditional to determine which HTML fragment to return.
    # In a real application, this data would likely come from a database.
    if name == "soup":
        # The HTML is returned directly as a string. FastAPI's HTMLResponse handles the headers.
        html_content = """<div class="text-center p-4 rounded-lg bg-yellow-900/30 border border-yellow-700"><svg class="mx-auto w-12 h-12 text-yellow-400 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.82m5.84-2.56a16.5 16.5 0 00-1.232-7.85 16.5 16.5 0 01-1.232 7.85m0 0a16.5 16.5 0 00-7.85-1.232 16.5 16.5 0 007.85 1.232m0 0a16.5 16.5 0 01-7.85 1.232 16.5 16.5 0 017.85-1.232M3 16.5v-4.82a6 6 0 015.84-7.38v4.82m5.84 2.56a16.5 16.5 0 01-7.85-1.232 16.5 16.5 0 017.85 1.232m-7.85 0a16.5 16.5 0 00-1.232 7.85m10.332-7.85a16.5 16.5 0 00-1.232-7.85m-1.232 7.85a16.5 16.5 0 01-1.232 7.85" /></svg><p class="text-lg font-semibold text-yellow-200">Soup of the Day</p><p class="text-yellow-400">Enjoy your hot and delicious soup!</p></div>"""
        return HTMLResponse(content=html_content)

    if name == "special":
        html_content = """<div class="text-center p-4 rounded-lg bg-cyan-900/30 border border-cyan-700"><svg class="mx-auto w-12 h-12 text-cyan-400 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg><p class="text-lg font-semibold text-cyan-200">Daily Special</p><p class="text-cyan-400">Perfectly grilled salmon with a side of asparagus.</p></div>"""
        return HTMLResponse(content=html_content)

    # It's good practice to handle unexpected inputs gracefully.
    return Response(status_code=404, content="Menu item not found")


@app.post("/custom-order", response_class=HTMLResponse)
async def post_custom_order(
    toppings: List[str] = Form(...),
    special_requests: str = Form("")
):
    """
    Handles POST requests from the 'build-a-burger' form.
    This endpoint demonstrates processing form data, including multiple values for a
    single field ('toppings'), and dynamically generating an HTML fragment in response.
    """
    # We dynamically build the list of toppings to be injected into the response HTML.
    # Using a list comprehension is a concise and Pythonic way to do this.
    toppings_li_elements = "".join([f"<li>{topping}</li>" for topping in toppings])

    # The final HTML response is constructed using an f-string. This is a modern
    # and readable way to format strings with embedded variables.
    response_html = f"""<div class="text-left p-4 rounded-lg bg-green-900/30 border border-green-700"><svg class="mx-auto w-12 h-12 text-green-400 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg><h3 class="text-lg font-semibold text-green-200 text-center mb-3">Your Custom Burger is Ready!</h3><div class="text-sm text-green-300 space-y-2"><p><strong class="font-medium text-green-200">Toppings:</strong></p><ul class="list-disc list-inside pl-2">{toppings_li_elements}</ul><p><strong class="font-medium text-green-200">Special Requests:</strong><br><span class="text-green-400 italic">"{special_requests or 'None'}"</span></p></div></div>"""

    # We update the global state with the details of this order.
    # This demonstrates how an API endpoint can modify the application state.
    app_state["last_order"] = response_html

    return HTMLResponse(content=response_html)