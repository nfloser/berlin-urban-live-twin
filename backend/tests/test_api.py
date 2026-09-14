"""Tests for the public backend API."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_reports_service_status(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_rejects_empty_twin_state(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "not_ready"


def test_state_endpoint_reports_loaded_twin_summary(tmp_path: Path) -> None:
    (tmp_path / "air.ttl").write_text(
        """
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/station/MC010> a city:AirQualityStation ;
            city:isActive true .
        """,
        encoding="utf-8",
    )
    client = TestClient(create_app(tmp_path))

    response = client.get("/state")

    assert response.status_code == 200
    assert response.json()["active_air_quality_stations"] == 1
