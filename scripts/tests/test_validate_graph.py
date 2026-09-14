"""Tests for SHACL validation before graph publication."""

from pathlib import Path

import pytest

from scripts.validate_graph import validate_integrated_graph


SHAPES = Path(__file__).resolve().parents[2] / "ontology" / "shapes.ttl"


def test_valid_weather_observation_conforms(tmp_path: Path) -> None:
    (tmp_path / "weather.ttl").write_text(
        """
        @prefix city: <https://example.org/berlin/ontology/> .
        @prefix prov: <http://www.w3.org/ns/prov#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <https://example.org/weather/1> a city:WeatherObservation ;
            city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime ;
            city:temperatureCelsius "18.2"^^xsd:double ;
            prov:wasDerivedFrom <https://api.brightsky.dev/current_weather> .
        """,
        encoding="utf-8",
    )

    assert validate_integrated_graph(tmp_path, SHAPES) > 0


def test_invalid_weather_observation_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "weather.ttl").write_text(
        """
        @prefix city: <https://example.org/berlin/ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <https://example.org/weather/1> a city:WeatherObservation ;
            city:observedAt "2026-09-14T08:00:00+00:00"^^xsd:dateTime .
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="SHACL validation"):
        validate_integrated_graph(tmp_path, SHAPES)
