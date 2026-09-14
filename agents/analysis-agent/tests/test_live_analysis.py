"""Tests for deriving urban stress from the shared RDF state."""

from pathlib import Path

import pytest

from app.live_analysis import derive_latest_urban_stress


def _write_state(
    tmp_path: Path,
    *,
    air_time: str,
    weather_time: str,
    transit_time: str,
) -> None:
    (tmp_path / "air-quality.ttl").write_text(
        f"""
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/lqi/a> a city:AirQualityIndexObservation ;
            city:observedAt "{air_time}"^^<http://www.w3.org/2001/XMLSchema#dateTime> ;
            city:airQualityGrade 2 .
        <https://example.org/lqi/b> a city:AirQualityIndexObservation ;
            city:observedAt "{air_time}"^^<http://www.w3.org/2001/XMLSchema#dateTime> ;
            city:airQualityGrade 4 .
        """,
        encoding="utf-8",
    )
    (tmp_path / "weather.ttl").write_text(
        f"""
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/weather/a> a city:WeatherObservation ;
            city:observedAt "{weather_time}"^^<http://www.w3.org/2001/XMLSchema#dateTime> ;
            city:temperatureCelsius 30.0 .
        """,
        encoding="utf-8",
    )
    (tmp_path / "transit.ttl").write_text(
        f"""
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/transit/a> a city:TransitObservation ;
            city:observedAt "{transit_time}"^^<http://www.w3.org/2001/XMLSchema#dateTime> ;
            city:delayedShare 0.25 .
        """,
        encoding="utf-8",
    )


def test_derives_stress_from_latest_cross_domain_observations(tmp_path: Path) -> None:
    _write_state(
        tmp_path,
        air_time="2026-09-14T08:00:00+00:00",
        weather_time="2026-09-14T08:30:00+00:00",
        transit_time="2026-09-14T08:45:00+00:00",
    )

    result, observed_at = derive_latest_urban_stress(tmp_path)

    assert result.air_quality_component == 0.6
    assert round(result.heat_component, 4) == 0.6667
    assert result.transit_component == 0.5
    assert round(result.index, 1) == 59.0
    assert observed_at.isoformat() == "2026-09-14T08:45:00+00:00"


def test_rejects_cross_domain_observations_more_than_two_hours_apart(tmp_path: Path) -> None:
    _write_state(
        tmp_path,
        air_time="2026-09-14T05:00:00+00:00",
        weather_time="2026-09-14T08:30:00+00:00",
        transit_time="2026-09-14T08:45:00+00:00",
    )

    with pytest.raises(ValueError, match="temporally inconsistent"):
        derive_latest_urban_stress(tmp_path)
