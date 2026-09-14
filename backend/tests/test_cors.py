"""Tests for browser access to the backend API."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_local_frontend_origin_is_allowed(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))

    response = client.options(
        "/stations",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
