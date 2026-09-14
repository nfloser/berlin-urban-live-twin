"""Tests for domain-specific API endpoints."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


FIXTURE = """
@prefix city: <https://example.org/berlin/ontology/> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/berlin/station/MC010> a city:AirQualityStation ;
    city:stationCode "MC010" ; city:name "010 Wedding" ; city:isActive true ;
    geo:lat "52.54291"^^xsd:double ; geo:long "13.34926"^^xsd:double .

<https://example.org/berlin/weather/1> a city:WeatherObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:temperatureCelsius "18.2"^^xsd:double ;
    city:relativeHumidityPercent "63.0"^^xsd:double .

<https://example.org/berlin/transit/1> a city:TransitObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:totalTripUpdates 200 ; city:delayedTripUpdates 40 ;
    city:maxDelaySeconds 420 ; city:delayedShare "0.2"^^xsd:double .
"""


def client_with_fixture(tmp_path: Path) -> TestClient:
    (tmp_path / "state.ttl").write_text(FIXTURE, encoding="utf-8")
    return TestClient(create_app(tmp_path))


def test_stations_endpoint_returns_map_ready_points(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/stations")
    assert response.status_code == 200
    assert response.json()[0]["code"] == "MC010"


def test_weather_endpoint_returns_latest_weather(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/weather")
    assert response.status_code == 200
    assert response.json()["temperature_c"] == 18.2


def test_transit_endpoint_returns_latest_realtime_summary(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/transit")
    assert response.status_code == 200
    assert response.json()["delayed_share"] == 0.2
