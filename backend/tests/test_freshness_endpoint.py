"""Tests for the source freshness API endpoint."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_freshness_endpoint_exposes_source_age_and_status(tmp_path: Path) -> None:
    now = datetime.now(timezone.utc)
    air = (now - timedelta(minutes=30)).isoformat()
    weather = (now - timedelta(minutes=20)).isoformat()
    transit = (now - timedelta(minutes=5)).isoformat()
    stress = (now - timedelta(minutes=4)).isoformat()

    (tmp_path / "state.ttl").write_text(
        f"""
        @prefix city: <https://example.org/berlin/ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <https://example.org/air/1> a city:AirQualityIndexObservation ; city:observedAt "{air}"^^xsd:dateTime .
        <https://example.org/weather/1> a city:WeatherObservation ; city:observedAt "{weather}"^^xsd:dateTime .
        <https://example.org/transit/1> a city:TransitObservation ; city:observedAt "{transit}"^^xsd:dateTime .
        <https://example.org/stress/1> a city:UrbanStressObservation ; city:observedAt "{stress}"^^xsd:dateTime .
        """,
        encoding="utf-8",
    )

    response = TestClient(create_app(tmp_path)).get("/freshness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["air_quality"]["status"] == "fresh"
    assert payload["weather"]["status"] == "fresh"
    assert payload["transit"]["status"] == "fresh"
    assert payload["urban_stress"]["status"] == "fresh"
