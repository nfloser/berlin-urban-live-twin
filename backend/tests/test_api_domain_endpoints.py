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

<https://example.org/berlin/lqi/MC010/1> a city:AirQualityIndexObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:observedAtStation <https://example.org/berlin/station/MC010> ;
    city:airQualityGrade 3 ; city:lqiPM10 2 ; city:lqiO3 3 .

<https://example.org/berlin/weather/1> a city:WeatherObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:temperatureCelsius "18.2"^^xsd:double ;
    city:relativeHumidityPercent "63.0"^^xsd:double .

<https://example.org/berlin/transit/1> a city:TransitObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:totalTripUpdates 200 ; city:delayedTripUpdates 40 ;
    city:maxDelaySeconds 420 ; city:delayedShare "0.2"^^xsd:double .

<https://example.org/berlin/derived/urban-stress/1> a city:UrbanStressObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:urbanStressIndex "31.0"^^xsd:double ;
    city:airQualityStressComponent "0.4"^^xsd:double ;
    city:heatStressComponent "0.0"^^xsd:double ;
    city:transitStressComponent "0.4"^^xsd:double .
"""


def client_with_fixture(tmp_path: Path) -> TestClient:
    (tmp_path / "state.ttl").write_text(FIXTURE, encoding="utf-8")
    return TestClient(create_app(tmp_path))


def test_stations_endpoint_returns_map_ready_points(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/stations")
    assert response.status_code == 200
    assert response.json()[0]["code"] == "MC010"


def test_air_quality_endpoint_returns_latest_official_lqi(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/air-quality")
    assert response.status_code == 200
    assert response.json()["worst_grade"] == 3
    assert response.json()["stations"][0]["station_code"] == "MC010"


def test_weather_endpoint_returns_latest_weather(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/weather")
    assert response.status_code == 200
    assert response.json()["temperature_c"] == 18.2


def test_transit_endpoint_returns_latest_realtime_summary(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/transit")
    assert response.status_code == 200
    assert response.json()["delayed_share"] == 0.2


def test_urban_stress_endpoint_returns_latest_derived_observation(tmp_path: Path) -> None:
    response = client_with_fixture(tmp_path).get("/urban-stress")
    assert response.status_code == 200
    assert response.json()["index"] == 31.0
    assert response.json()["air_quality_component"] == 0.4
