![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green.svg)
![HTMX](https://img.shields.io/badge/HTMX-1.9.10-blueviolet.svg)
![Pytest](https://img.shields.io/badge/Tests-Pytest%20%7C%20Playwright-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A curated suite of 22 self-contained, interactive learning modules designed to teach the core concepts of HTMX. Each module uses a real-world analogy to demonstrate how HTMX simplifies modern web development.

## About The Project

This repository contains a collection of mini-applications, each designed to isolate and teach specific HTMX features in a hands-on environment. The "by-example" philosophy means you learn by seeing and interacting with a fully functional, tested codebase.

Each module is a complete FastAPI application with a corresponding frontend and test suite. The project began as an experiment in LLM-driven development and has been systematically refined by a human developer to ensure quality, consistency, and pedagogical value.

### Core Features

- **22 Thematic Learning Modules:** From a "Personal Chef" to a "Chemistry Lab," each module uses a unique theme to make abstract concepts tangible.
- **Self-Contained & Isolated:** Every module is a standalone application, allowing you to focus on one set of concepts at a time.
- **Interactive UI:** The frontend is built with HTMX and Tailwind CSS, featuring instructional modals that explain both the "what" and the "why" of each feature.
- **Robust FastAPI Backend:** A simple and clear Python backend powers each module.
- **Full Test Coverage:** Includes both API-level tests (`pytest`) and end-to-end browser tests (`playwright`) to guarantee functionality.

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** HTMX, Tailwind CSS
- **Testing:** Pytest, Playwright
- **Tooling:** Python

## Getting Started

To run any of the learning modules locally, follow these steps.

### Prerequisites

- Python 3.10+
- pip (Python package installer)

### Installation & Running a Module

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/htmx-by-example.git
    cd htmx-by-example
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    # For Unix/macOS
    python -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    _(Note: A single `requirements.txt` in the root may be added later. For now, install the core packages.)_

    ```bash
    pip install fastapi "uvicorn[standard]" jinja2 pytest playwright
    playwright install chromium # Install the necessary browser for E2E tests
    ```

4.  **Navigate to a module and run the server:**
    Let's run the "Personal Chef" module (`001`).

    ```bash
    cd CW_HTMX_ESSENTIALS/001
    uvicorn app.main:app --reload
    ```

5.  **Open the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000`. You should now see the interactive courseware module.

## Running the Tests

Each module comes with its own test suite. To run the tests for a specific module, navigate to its directory and use `pytest`.

```bash
# Example for module 001
cd CW_HTMX_ESSENTIALS/001
pytest -v
```

## Project Structure

The repository is organized into a main directory containing all the courseware modules.

```
htmx-by-example/
├── CW_HTMX_ESSENTIALS/
│   ├── 001/                  # Module 001: Personal Chef
│   │   ├── app/              # Source code for the FastAPI application
│   │   │   ├── templates/    # HTML templates and partials
│   │   │   └── main.py       # The main FastAPI application
│   │   ├── tests/            # API and E2E tests
│   │   └── ...
│   ├── 002/                  # Module 002: Stage Manager
│   │   └── ...
│   └── ...                   # And so on for all 22 modules
│
├── enhance_courseware.py     # Utility script for managing modules
└── README.md
```

## Utility Scripts

This repository includes scripts to help manage and enhance the courseware modules.

### `enhance_courseware.py`

This Python script programmatically injects the instructional modal system (`Set the Scene` and `The "Why" Behind the "What"`) into a target module's `index.html`. It is idempotent, meaning it can be run multiple times without creating duplicate code.

**Usage:**

```bash
# First, ensure you have BeautifulSoup installed:
pip install beautifulsoup4

# Run the script from the repository root, pointing to a module
python enhance_courseware.py ./CW_HTMX_ESSENTIALS/001
```

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Acknowledgments

- [HTMX](https://htmx.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Pytest](https://pytest.org/)
- [Playwright](https://playwright.dev/)
