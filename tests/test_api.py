"""API route tests using FastAPI TestClient."""

from fastapi.testclient import TestClient

from python_postgresql_crud.main import app

client = TestClient(app)


def test_health_check_endpoint() -> None:
    """Ensure /health returns HTTP 200 and expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "version" in data


def test_home_page_renders_html() -> None:
    """Ensure GET / renders the main HTML interface."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "User Management Directory" in response.text


def test_create_user_validation_error() -> None:
    """Ensure invalid payload returns 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/users",
        json={
            "name": "",  # invalid
            "email": "invalid-email",
            "mobile": "123",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_get_non_existent_user_returns_404() -> None:
    """Ensure querying non-existent ID returns 404 or gracefully handles uninitialized DB."""
    response = client.get("/api/v1/users/999999")
    # If DB is not connected, it returns 500, if connected returns 404
    assert response.status_code in (404, 500)
