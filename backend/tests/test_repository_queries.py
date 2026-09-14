"""Tests for domain-specific queries over the integrated RDF state."""

from pathlib import Path

from app.repository import TwinRepository


FIXTURE = """
@prefix city: <https://example.org/berlin/ontology/> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/berlin/station/MC010> a city:AirQualityStation ;
    city:stationCode "MC010" ;
    city:name "010 Wedding" ;
    city:isActive true ;
    geo:lat "52.54291"^^xsd:double ;
    geo:long "13.34926"^^xsd:double .

<https://example.org/berlin/weather/2026-09-14T08:00:00+00:00> a city:WeatherObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:temperatureCelsius "18.2"^^xsd:double ;
    city:relativeHumidityPercent "63.0"^^xsd:double ;
    prov:wasDerivedFrom <https://api.brightsky.dev/current_weather> .

<https://example.org/berlin/transit/2026-09-14T08:00:00+00:00> a city:TransitObservation ;
    city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
    city:totalTripUpdates 200 ;
    city:delayedTripUpdates 40 ;
    city:maxDelaySeconds 420 ;
    city:delayedShare "0.2"^^xsd:double ;
    prov:wasDerivedFrom <https://production.gtfsrt.vbb.de/data> .
"""


def repository_with_fixture(tmp_path: Path) -> TwinRepository:
    (tmp_path / "state.ttl").write_text(FIXTURE, encoding="utf-8")
    repository = TwinRepository(tmp_path)
    repository.reload()
    return repository


def test_active_stations_returns_map_ready_station_data(tmp_path: Path) -> None:
    repository = repository_with_fixture(tmp_path)

    assert repository.active_stations() == [
        {
            "code": "MC010",
            "name": "010 Wedding",
            "latitude": 52.54291,
            "longitude": 13.34926,
        }
    ]


def test_latest_weather_returns_most_recent_weather_values(tmp_path: Path) -> None:
    repository = repository_with_fixture(tmp_path)

    weather = repository.latest_weather()

    assert weather == {
        "observed_at": "2026-09-14T08:00:00+00:00",
        "temperature_c": 18.2,
        "relative_humidity_pct": 63.0,
    }


def test_latest_transit_returns_realtime_summary(tmp_path: Path) -> None:
    repository = repository_with_fixture(tmp_path)

    transit = repository.latest_transit()

    assert transit == {
        "observed_at": "2026-09-14T08:00:00+00:00",
        "total_trip_updates": 200,
        "delayed_trip_updates": 40,
        "max_delay_seconds": 420,
        "delayed_share": 0.2,
    }


def test_provenance_summary_returns_source_lineage(tmp_path: Path) -> None:
    repository = repository_with_fixture(tmp_path)

    assert repository.provenance_summary() == [
        {
            "observation_type": "TransitObservation",
            "source": "https://production.gtfsrt.vbb.de/data",
            "count": 1,
        },
        {
            "observation_type": "WeatherObservation",
            "source": "https://api.brightsky.dev/current_weather",
            "count": 1,
        },
    ]
