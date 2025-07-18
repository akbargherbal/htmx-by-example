# This file defines the main FastAPI application, which serves as the backend API
# for our HTMX-powered frontend. It follows the principle of ephemeral state,
# meaning all data is stored in simple Python variables and is reset on restart.
# This is an educational choice to focus solely on the API and HTMX interaction
# without the complexity of a database.

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the main FastAPI application.
app = FastAPI()

# Configure Jinja2 to look for templates in the 'app/templates' directory.
# This is essential for serving the initial HTML page.
templates = Jinja2Templates(directory="app/templates")

# --- Ephemeral State Management ---

# In a real application, this would be a database model. For this educational
# project, we use a simple dictionary to represent the application's state.
# This keeps the focus on the API contract and HTMX.
# The initial state is an empty dictionary, as no actions have been taken yet.
app_state = {}

def reset_state_for_testing():
    """
    Resets the in-memory state. This is a critical function for ensuring
    that our automated tests run in isolation, each starting from a clean slate.
    It is called automatically by a pytest fixture before each test.
    """
    global app_state
    app_state = {}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Application Entrypoint ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the user's entry point to the
    application. It passes the current application state to the template,
    allowing Jinja2 to render the initial UI.
    """
    # The context dictionary makes Python variables available inside the HTML template.
    return templates.TemplateResponse(
        request=request, name="index.html", context={"initial_state": app_state}
    )


# --- API Endpoints (Implementing the API Contract) ---

@app.post("/register/success", response_class=HTMLResponse)
async def register_success():
    """
    Handles a successful course registration.
    Returns a 200 OK status and an HTML fragment confirming the registration.
    This simulates a successful state change on the server.
    """
    # The HTML is returned directly as a string. FastAPI, with response_class=HTMLResponse,
    # will correctly set the Content-Type header to 'text/html'.
    html_content = """
    <div id="main-content-after-success" data-testid="main-content-after-success" class="bg-gray-800 border border-gray-700 p-6 rounded-xl shadow-lg">
      <h2 class="text-2xl font-semibold mb-4 text-green-400">My Fall Schedule</h2>
      <p class="text-gray-400 mb-4">You have successfully registered for the following course:</p>
      <ul class="list-disc list-inside bg-gray-900 p-4 rounded-lg">
        <li class="text-lg">BIOL-101: Introduction to Biology</li>
      </ul>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)

@app.post("/register/full", response_class=HTMLResponse)
async def register_full():
    """
    Handles a failed course registration due to the course being full.
    Returns a 409 Conflict status code, which is appropriate for indicating
    that the request could not be completed because of a conflict with the
    current state of the resource (the course is full).
    """
    html_content = """
    <div data-testid="registration-error-target-after-action" class="min-h-[2rem] p-2 bg-red-900/50 border border-red-500 rounded-md">
      <p class="text-red-400 font-semibold">Error: Course is full.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_409_CONFLICT)

@app.get("/records/grades/forbidden", response_class=HTMLResponse)
async def get_grades_forbidden():
    """
    Simulates an attempt to access a resource that the user is not authorized to see.
    Returns a 403 Forbidden status, the standard response for valid requests that
    the server understands but refuses to authorize.
    """
    html_content = """
    <div data-testid="records-result-target-after-403" class="bg-red-900/50 border border-red-500 rounded-lg p-4 min-h-[6rem]">
      <h4 class="font-bold text-red-300">Access Denied (403 Forbidden)</h4>
      <p class="text-red-400">You do not have permission to view grades for this student.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_403_FORBIDDEN)

@app.get("/records/transcript/not-found", response_class=HTMLResponse)
async def get_transcript_not_found():
    """
    Simulates a request for a resource that does not exist.
    Returns a 404 Not Found status, which is the standard way to indicate
    that the server cannot find the requested resource.
    """
    html_content = """
    <div data-testid="records-result-target-after-404" class="bg-red-900/50 border border-red-500 rounded-lg p-4 min-h-[6rem]">
      <h4 class="font-bold text-red-300">Not Found (404)</h4>
      <p class="text-red-400">The requested transcript for the specified student ID does not exist.</p>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_404_NOT_FOUND)

@app.get("/records/grades/payment-due")
async def get_grades_payment_due():
    """
    Simulates a scenario where access to a resource triggers a client-side redirect.
    It returns a 200 OK status but includes the special 'HX-Redirect' header.
    HTMX will see this header and automatically navigate the browser to the
    specified URL ('/pay-tuition'). The response body is empty as it won't be used.
    """
    return Response(status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/pay-tuition"})

@app.get("/pay-tuition", response_class=HTMLResponse)
async def pay_tuition_page():
    """
    This endpoint serves the page that the user is redirected to.
    It returns a 200 OK status and the full HTML for the payment page, which
    will replace the entire page content due to the HTMX redirect.
    """
    html_content = """
    <div id="main-content-after-redirect" data-testid="main-content-after-redirect" class="bg-gray-800 border-2 border-yellow-500 p-6 rounded-xl shadow-lg">
      <h2 class="text-2xl font-semibold mb-4 text-yellow-400">Tuition Payment Required</h2>
      <p class="text-gray-400 mb-4">Access to student records is blocked until your outstanding tuition balance is paid. Please clear your balance to proceed.</p>
      <div class="mt-6">
        <button class="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg text-lg">Pay Tuition Now</button>
      </div>
    </div>
    """
    return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)