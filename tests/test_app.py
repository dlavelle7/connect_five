import pytest

from src.server import app


@pytest.fixture
def client():
    """Test client for testing requests to the application."""
    app.app.config['TESTING'] = True
    client = app.app.test_client()
    yield client


def test_state_endpoint(client):
    response = client.get("/state")
    assert response.status_code == 200
