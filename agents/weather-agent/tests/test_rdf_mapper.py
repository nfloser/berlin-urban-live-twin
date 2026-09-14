"""Tests for semantic weather representation."""

from datetime import datetime

from rdflib import RDF, XSD, Literal, URIRef

from app.models import WeatherObservation
from app.rdf_mapper import CITY, weather_to_graph


def test_weather_to_graph_creates_observation_triples() -> None:
    observation = WeatherObservation(
        observed_at=datetime.fromisoformat("2026-09-14T08:00:00+00:00"),
        temperature_c=18.2,
        relative_humidity_pct=63.0,
        pressure_hpa=1017.4,
        wind_speed_kmh=11.5,
        condition="dry",
    )

    graph = weather_to_graph(observation)
    subject = URIRef("https://example.org/berlin/weather/2026-09-14T08:00:00+00:00")

    assert (subject, RDF.type, CITY.WeatherObservation) in graph
    assert (subject, CITY.temperatureCelsius, Literal(18.2, datatype=XSD.double)) in graph
    assert (subject, CITY.relativeHumidityPercent, Literal(63.0, datatype=XSD.double)) in graph
