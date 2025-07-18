# This file defines the core FastAPI application, its endpoints, and state management.
# As a Principal Engineer, I emphasize clean separation of concerns, but for this
# educational example, we keep everything in one file for simplicity.
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the central object that will handle
# all incoming web requests.
app = FastAPI()

# Configure Jinja2 for server-side HTML templating. This allows us to inject
# dynamic data from the backend into our HTML files. The directory is set to
# 'app/templates' where our index.html will reside.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# In a real-world application, state would be managed in a database (e.g., PostgreSQL, Redis).
# For this educational project, we use a simple in-memory dictionary to hold application state.
# This makes the example self-contained and easy to run without external dependencies.
# NOTE: This state is ephemeral and will be lost if the server restarts.
app_state = {"request_count": 0}

def reset_state_for_testing():
    """
    Resets the application's in-memory state to its initial condition.
    This is a critical function for ensuring that our automated tests run in an
    isolated environment, preventing results from one test from influencing another.
    """
    global app_state
    app_state = {"request_count": 0}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the primary entrypoint for users
    accessing the application via a web browser. It passes the initial application
    state to the template for rendering.
    """
    # The context dictionary maps variable names in the template to Python variables here.
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_state_variable": app_state}
    )


# --- API Endpoints ---

@app.post("/process-address-change", response_class=HTMLResponse)
async def process_address_change(
    street: str = Form(...),
    zip_code: str = Form(...),
    customer_id: str = Form(..., alias="customer-id"), # Use alias for form fields with hyphens
    service_type: str = Form(...)
):
    """
    Handles a successful form submission for an address change.
    It extracts data from the form payload and returns an HTML fragment
    confirming the successful processing of the request.
    """
    # In a real application, this is where you would validate the data,
    # interact with a database, and call other services. Here, we simply
    # format the success response.
    html_content = f"""
    <div class="p-4 bg-green-900/50 border border-green-700 rounded-md text-green-300">
      <h4 class="font-bold">Success!</h4>
      <p>Request processed for customer {customer_id} (Service: {service_type}).</p>
      <p>Address successfully updated to {street}, {zip_code}.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/process-invalid-zip", response_class=HTMLResponse)
async def process_invalid_zip():
    """
    Simulates a 'Not Found' error, as if a submitted zip code was invalid.
    This endpoint demonstrates how to return a non-200 status code with an
    HTML fragment, which HTMX can then place into the DOM.
    """
    html_content = """
    <div class="p-4 bg-red-900/50 border border-red-700 rounded-md text-red-300">
      <h4 class="font-bold">Error: Not Found (404)</h4>
      <p>The destination zip code could not be found. Please check the address and try again.</p>
    </div>
    """
    # It's crucial to set the status_code on the response so that HTMX and other
    # tools can correctly interpret the result of the HTTP request.
    return HTMLResponse(content=html_content, status_code=404)

@app.post("/simulate-server-failure", response_class=HTMLResponse)
async def simulate_server_failure():
    """
    Simulates a critical 'Internal Server Error'. This is useful for testing
    how the frontend handles unexpected backend failures.
    """
    html_content = """
    <div class="p-4 bg-yellow-900/50 border border-yellow-700 rounded-md text-yellow-300">
      <h4 class="font-bold">Error: Internal Server Error (500)</h4>
      <p>The mail sorting machine is offline. We are unable to process your request at this time. Please try again later.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=500)