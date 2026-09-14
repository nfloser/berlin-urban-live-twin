"""Read the shared RDF state and derive the latest urban-stress observation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from rdflib import Graph

from app.urban_stress import UrbanStressResult, calculate_urban_stress

MAX_SOURCE_TIME_SPREAD = timedelta(hours=2)


def _load_graph(data_directory: Path) -> Graph:
    graph = Graph()
    for name in ("air-quality.ttl", "weather.ttl", "transit.ttl"):
        path = data_directory / name
        if path.exists():
            graph.parse(path, format="turtle")
    return graph


def derive_latest_urban_stress(data_directory: Path) -> tuple[UrbanStressResult, datetime]:
    """Derive stress only from sufficiently time-aligned domain observations.

    Air quality uses the worst current station LQI as a conservative city-level
    signal. Weather and transit use their latest available observations. The
    three source timestamps may differ by at most two hours so that the result
    does not combine materially stale and current conditions.
    """
    graph = _load_graph(data_directory)

    air_query = """
    PREFIX city: <https://example.org/berlin/ontology/>
    SELECT (MAX(?grade) AS ?grade) (MAX(?observedAt) AS ?observedAt)
    WHERE {
        ?observation a city:AirQualityIndexObservation ;
                     city:airQualityGrade ?grade ;
                     city:observedAt ?observedAt .
    }
    """
    weather_query = """
    PREFIX city: <https://example.org/berlin/ontology/>
    SELECT ?temperature ?observedAt
    WHERE {
        ?observation a city:WeatherObservation ;
                     city:temperatureCelsius ?temperature ;
                     city:observedAt ?observedAt .
    }
    ORDER BY DESC(?observedAt)
    LIMIT 1
    """
    transit_query = """
    PREFIX city: <https://example.org/berlin/ontology/>
    SELECT ?delayedShare ?observedAt
    WHERE {
        ?observation a city:TransitObservation ;
                     city:delayedShare ?delayedShare ;
                     city:observedAt ?observedAt .
    }
    ORDER BY DESC(?observedAt)
    LIMIT 1
    """

    air = next(iter(graph.query(air_query)), None)
    weather = next(iter(graph.query(weather_query)), None)
    transit = next(iter(graph.query(transit_query)), None)
    if air is None or air[0] is None or weather is None or transit is None:
        raise ValueError("Cross-domain stress requires LQI, weather, and transit observations")

    timestamps = [
        datetime.fromisoformat(str(air[1]).replace("Z", "+00:00")),
        datetime.fromisoformat(str(weather[1]).replace("Z", "+00:00")),
        datetime.fromisoformat(str(transit[1]).replace("Z", "+00:00")),
    ]
    if max(timestamps) - min(timestamps) > MAX_SOURCE_TIME_SPREAD:
        raise ValueError("Cross-domain observations are temporally inconsistent")

    result = calculate_urban_stress(
        air_quality_grade=float(air[0]),
        temperature_c=float(weather[0]),
        delayed_share=float(transit[0]),
    )
    return result, max(timestamps)
