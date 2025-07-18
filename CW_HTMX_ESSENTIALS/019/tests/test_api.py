# This file contains the API tests for our FastAPI application.
# The goal is to verify that each endpoint behaves exactly as defined in the API Contract.
# We use FastAPI's TestClient, which provides a simple and effective way to
# make requests to the application without needing a running server.

import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state_for_testing, SONGS

# This fixture is a cornerstone of reliable testing. By using `autouse=True`,
# it automatically runs before every single test function in this file.
# This guarantees that each test starts with a clean, predictable state,
# preventing tests from interfering with one another.
@pytest.fixture(autouse=True)
def reset_state_before_each_test():
    """Pytest fixture to automatically reset state before each test."""
    reset_state_for_testing()

# We instantiate the TestClient once at the module level.
# This is efficient as it sets up the client a single time for all tests in this file.
client = TestClient(app)


# --- Test Functions ---

def test_enable_jukebox_returns_enabled_song_selectors():
    """
    Verifies that POST /enable-jukebox correctly changes the state and
    returns the HTML fragment for the enabled song selectors, as per the contract.
    """
    # 1. Arrange & Act: Make the request to the endpoint.
    response = client.post("/enable-jukebox")

    # 2. Assert: Verify the response against the API Contract.
    assert response.status_code == 200
    # Check for the main container's test ID.
    assert 'data-testid="song-selectors-enabled"' in response.text
    # Check for a specific, known song to ensure the loop is working.
    assert 'data-testid="song-B5-select-enabled"' in response.text
    assert 'data-testid="song-C1-select-enabled"' in response.text
    assert "Johnny B. Goode" in response.text


def test_preview_song_returns_correct_song_details():
    """
    Verifies that GET /songs/preview returns a 200 OK and the correct
    HTML fragment containing details for the requested song.
    """
    # 1. Arrange: Define the song we want to preview.
    song_id_to_test = "B5"
    expected_song = SONGS[song_id_to_test]

    # 2. Act: Make the request to the endpoint with the songId as a query parameter.
    response = client.get(f"/songs/preview?songId={song_id_to_test}")

    # 3. Assert: Verify the response.
    assert response.status_code == 200
    assert 'data-testid="main-display-after-preview"' in response.text
    assert f"Song: {expected_song['name']}" in response.text
    assert f"Runtime: {expected_song['runtime']}" in response.text


def test_preview_nonexistent_song_returns_404():
    """
    Tests the failure case for the preview endpoint. A robust API must
    gracefully handle requests for resources that do not exist.
    """
    # 1. Arrange & Act: Request a song ID that we know is not in our data.
    response = client.get("/songs/preview?songId=Z9")

    # 2. Assert: Verify that the server responds with a 404 Not Found.
    assert response.status_code == 404


def test_queue_song_returns_new_list_item():
    """
    Verifies that POST /songs/queue correctly adds a song to the queue
    and returns the corresponding HTML `<li>` fragment.
    """
    # 1. Arrange: Define the song we want to queue.
    song_id_to_test = "C1"
    expected_song = SONGS[song_id_to_test]
    # The payload for a POST request with form data.
    form_data = {"songId": song_id_to_test}

    # 2. Act: Make the POST request.
    response = client.post("/songs/queue", data=form_data)

    # 3. Assert: Verify the response fragment.
    assert response.status_code == 200
    # The test ID should be specific to the item, enabling precise testing.
    assert f'data-testid="queue-item-{song_id_to_test}"' in response.text
    assert f"{song_id_to_test} - {expected_song['name']}" in response.text.strip()


def test_queue_nonexistent_song_returns_404():
    """
    Tests the failure case for the queue endpoint, ensuring the API
    rejects attempts to queue songs that are not in the system.
    """
    # 1. Arrange & Act: Attempt to queue a song ID that does not exist.
    response = client.post("/songs/queue", data={"songId": "Z9"})

    # 2. Assert: Verify the expected 404 Not Found response.
    assert response.status_code == 404