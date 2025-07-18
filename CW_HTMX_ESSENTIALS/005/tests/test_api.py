# This file contains the API-level tests for our FastAPI application.
# The primary goal is to verify that each endpoint strictly conforms to the
# API Contract. We use FastAPI's TestClient, which provides a simple and
# direct way to make requests to the application without needing a live server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing

# --- Test Setup ---

# Per the testing guide, we instantiate the TestClient once at the module level.
# This is efficient and sufficient for our needs, as the client itself is stateless.
# It wraps our FastAPI 'app' object.
client = TestClient(app)

# This fixture is the cornerstone of test isolation. The 'autouse=True' argument
# ensures it runs automatically before every single test function in this file.
# By calling 'reset_state_for_testing', we guarantee that no state from a
# previous test can leak into and affect the outcome of a subsequent test.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()


# --- Test Functions ---

def test_get_lego_pilot_returns_correct_fragment():
    """
    Verifies that the GET /lego/pilot endpoint returns a 200 OK status
    and the exact HTML fragment for the pilot, as specified in the contract.
    """
    # 1. Arrange & Act: Make the HTTP request to the endpoint.
    response = client.get("/lego/pilot")

    # 2. Assert: Verify the response meets the contract's requirements.
    assert response.status_code == 200
    assert response.text == "<span>LEGO Pilot</span>"
    assert response.headers["content-type"] == "text/html; charset=utf-8"


def test_get_lego_window_wall_returns_correct_fragment():
    """
    Verifies that the GET /lego/window-wall endpoint returns a 200 OK status
    and the HTML fragment for the window wall. We check for key attributes
    to ensure the correct element is returned.
    """
    # 1. Arrange & Act
    response = client.get("/lego/window-wall")

    # 2. Assert
    assert response.status_code == 200
    # Instead of matching the exact multiline string (which can be brittle),
    # we assert the presence of key identifiers and content.
    assert 'id="wall-section-1"' in response.text
    assert 'data-testid="wall-section-1-final"' in response.text
    assert "Window Wall" in response.text
    assert 'bg-cyan-300' in response.text # Check for the window element


def test_get_lego_top_brick_returns_correct_fragment():
    """
    Verifies that the GET /lego/top-brick endpoint returns a 200 OK status
    and the HTML fragment for the red brick.
    """
    # 1. Arrange & Act
    response = client.get("/lego/top-brick")

    # 2. Assert
    assert response.status_code == 200
    assert 'bg-red-500' in response.text
    assert '>Brick<' in response.text


def test_get_lego_tree_returns_correct_fragment():
    """
    Verifies that the GET /lego/tree endpoint returns a 200 OK status
    and the composite HTML fragment for the tree.
    """
    # 1. Arrange & Act
    response = client.get("/lego/tree")

    # 2. Assert
    assert response.status_code == 200
    assert 'data-testid="tree"' in response.text
    assert 'bg-green-700' in response.text # Check for the treetop
    assert 'bg-amber-800' in response.text # Check for the trunk


def test_get_castle_instructions_returns_full_document():
    """
    Verifies that the GET /lego/castle-instructions endpoint returns a 200 OK
    and a full HTML document containing the specific element (`#drawbridge-piece`)
    that the frontend will need to select.
    """
    # 1. Arrange & Act
    response = client.get("/lego/castle-instructions")

    # 2. Assert
    assert response.status_code == 200
    # We verify that this is a full HTML document.
    assert "<html>" in response.text
    assert "<body>" in response.text
    # Most importantly, we verify the presence of the source element that
    # hx-select will target.
    assert 'id="drawbridge-piece"' in response.text
    assert 'data-testid="source-drawbridge"' in response.text
    assert "... a wooden drawbridge ..." in response.text