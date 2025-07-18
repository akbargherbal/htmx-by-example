# This file defines the main FastAPI application, which serves as the backend for our HTMX example.
# It's designed to be a single-file, self-contained server for educational purposes.

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# The `app` instance is the core of our API. All API routes will be registered with it.
app = FastAPI()

# We configure Jinja2Templates to load HTML files from the `app/templates` directory.
# This allows us to separate our HTML presentation from our Python logic.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# PRINCIPAL ENGINEER's NOTE:
# For this educational project, we are explicitly avoiding a database.
# All application "state" is stored in a simple global variable.
# This is NOT a production-ready approach, but it's perfect for demonstrating
# specific backend concepts without the overhead of a database setup.
# The state here represents the initial content of the "inbox" on the frontend.
inbox_content: str

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its default.
    This is a critical function for ensuring our automated tests run in a clean,
    isolated environment. It's called automatically before each test case.
    """
    global inbox_content
    # The initial state is an empty div, representing an empty inbox.
    inbox_content = '<div data-testid="inbox-initial-state" class="p-4 text-slate-500">Inbox is currently empty.</div>'

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main `index.html` page.
    This is the primary entry point for users accessing the application in a browser.
    It passes the current application state (`inbox_content`) to the template.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_inbox_content": inbox_content}
    )


# --- API Endpoints (as per API Contract) ---

@app.get("/request-file/missing", response_class=HTMLResponse)
async def request_missing_file():
    """
    Simulates a "Not Found" error, as defined in the API contract.
    This endpoint returns a 404 status code directly, along with a specific
    HTML fragment that HTMX will place into the target element.
    """
    html_content = """
    <div data-testid="inbox-404-state" class="p-4 bg-yellow-900/50 border border-yellow-700 rounded-md text-yellow-300">
        <p class="font-bold">Memo: Request Failure</p>
        <p>File Not Found. The requested employee file does not exist.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=404)


@app.get("/request/crashed-server", response_class=HTMLResponse)
async def request_crashed_server():
    """
    Simulates an "Internal Server Error", as defined in the API contract.
    This demonstrates how HTMX can handle 5xx server-side errors gracefully.
    The endpoint returns a 500 status code and a user-friendly error message in HTML.
    """
    html_content = """
    <div class="p-4 bg-red-900/50 border border-red-700 rounded-md text-red-300">
        <p class="font-bold">Server Error</p>
        <p>Records Department is currently offline.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=500)


@app.get("/mail/old-department")
async def request_redirect():
    """
    Simulates a request to an old endpoint that needs to be redirected.
    Instead of returning HTML, this endpoint returns a special `HX-Redirect` header.
    HTMX will see this header and automatically make a new GET request to the
    URL specified in the header's value. The response body is empty.
    """
    # We return a standard Response object so we can manually set the headers.
    # The status code is 200 OK, as the instruction to redirect was successful.
    return Response(status_code=200, headers={"HX-Redirect": "/mail/new-department"})


@app.get("/mail/new-department", response_class=HTMLResponse)
async def get_new_department_mail():
    """
    This is the target of the `HX-Redirect`.
    It returns the final, successful HTML fragment that the user should see
    after their initial request was rerouted.
    """
    html_content = """
    <div data-testid="inbox-redirect-state" class="p-4 bg-green-900/50 border border-green-700 rounded-md text-green-300">
        <p class="font-bold">Memo: Request Update</p>
        <p>Your request was rerouted and received by the correct department.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=200)