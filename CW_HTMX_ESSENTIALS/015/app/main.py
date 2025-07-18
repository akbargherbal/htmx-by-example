# app/main.py

# This file defines the core FastAPI application, including state management,
# routing, and request handling logic. As a Principal Engineer, I emphasize
# keeping this file clean and focused on the API contract. Business logic
# should be clearly separated within endpoint functions.

import re
from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# --- Application Setup ---

# Instantiate the FastAPI application. This is the central object that
# powers all API functionality.
app = FastAPI()

# Configure Jinja2 for server-side HTML templating. This is crucial for
# rendering the initial page (`index.html`) and any full-page responses.
# The directory is specified relative to the application's root.
templates = Jinja2Templates(directory="app/templates")


# --- In-Memory State Management ---

# As per the project scope, we use a simple in-memory dictionary for state.
# This is suitable for educational examples but would be replaced by a
# proper database (e.g., PostgreSQL with SQLAlchemy) in a production system.
# The state holds the details of the most recently requested book.
_LAST_REQUESTED_BOOK = {}

def reset_state_for_testing():
    """
    Resets the application's in-memory state. This utility is essential for
    ensuring that automated tests run in isolation, starting from a known,
    clean state for each test case.
    """
    global _LAST_REQUESTED_BOOK
    _LAST_REQUESTED_BOOK = {}

# Initialize the state when the application starts.
reset_state_for_testing()


# --- Helper Functions ---

def _slugify(text: str) -> str:
    """
    A simple utility to convert a string into a URL-friendly "slug".
    This is a common requirement for creating clean, readable URLs.
    1. Convert to lowercase.
    2. Remove non-word characters (everything except numbers and letters).
    3. Replace whitespace with a single hyphen.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text

def _generate_book_response_html(title: str, author: str, slug: str) -> str:
    """
    Generates the standard HTML fragment for a book.
    Centralizing HTML generation in a single function ensures consistency
    between the POST and GET endpoints, adhering to the DRY principle.
    """
    return f"""
<div id="librarian-desk-response" data-testid="librarian-desk-response-final" class="mt-4 p-4 bg-green-900/50 border border-green-700 rounded-md">
 <h4 class="font-bold text-lg text-green-400">Request Fulfilled!</h4>
 <p class="text-gray-300 mt-2">The book <strong class="text-white">{title}</strong> by <strong class="text-white">{author}</strong> is now available for you.</p>
 <p class="text-xs text-gray-400 mt-3">Note: The browser URL has been updated to <code class="bg-gray-800 text-sm p-1 rounded">/book/{slug}</code> for bookmarking.</p>
</div>
"""

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html page. This is the application's entrypoint.
    It passes the current application state to the template, allowing Jinja2
    to render the initial UI correctly.
    """
    # The context dictionary makes Python variables available inside the HTML template.
    return templates.TemplateResponse(
        request=request, name="index.html", context={"book": _LAST_REQUESTED_BOOK}
    )

@app.post("/request-book", response_class=HTMLResponse)
async def request_book(
    response: Response,
    title: str = Form(...),
    author: str = Form(...)
):
    """
    Handles the form submission to request a new book.
    It updates the application state and returns an HTML fragment.
    Crucially, it also sets the `HX-Push-Url` header to update the browser's
    URL bar, a key feature for creating bookmarkable HTMX-powered pages.
    """
    # Generate a URL-friendly slug from the book title.
    book_slug = _slugify(title)

    # Update the global state with the new book's details.
    _LAST_REQUESTED_BOOK.update({
        "title": title,
        "author": author,
        "slug": book_slug
    })

    # Set the HTMX header to push a new URL to the browser's history.
    # This is the core of the "Deep Linking" pattern.
    response.headers["HX-Push-Url"] = f"/book/{book_slug}"

    # Generate and return the HTML fragment.
    html_content = _generate_book_response_html(title, author, book_slug)
    return HTMLResponse(content=html_content)


@app.get("/book/{book_slug}", response_class=HTMLResponse)
async def get_book_by_slug(book_slug: str):
    """
    Allows direct access to a book's state via its slug.
    This endpoint makes the URL pushed by the POST request "real" and
    bookmarkable. It retrieves the state and renders the same fragment.
    """
    # In a real app, we'd query the database for `book_slug`. Here, we
    # simply retrieve it from our in-memory state.
    # This assumes the state is already populated, which is a valid
    # assumption for the defined user flow and tests.
    title = _LAST_REQUESTED_BOOK.get("title", "Unknown Title")
    author = _LAST_REQUESTED_BOOK.get("author", "Unknown Author")

    # Generate and return the same consistent HTML fragment.
    html_content = _generate_book_response_html(title, author, book_slug)
    return HTMLResponse(content=html_content)