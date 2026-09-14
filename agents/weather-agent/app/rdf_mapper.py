"""RDF mapping for weather observations."""

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.models import WeatherObservation

CITY = Namespace("https://example.org/berlin/ontology/")
WEATHER_BASE = "https://example.org/berlin/weather/"


def weather_to_graph(observation: WeatherObservation) -> Graph:
    """Create an RDF graph for one Berlin weather observation."""
    graph = Graph()
    graph.bind("city", CITY)

    subject = URIRef(f"{WEATHER_BASE}{observation.observed_at.isoformat()}")
    graph.add((subject, RDF.type, CITY.WeatherObservation))
    graph.add(
        (
            subject,
            CITY.observedAt,
            Literal(observation.observed_at.isoformat(), datatype=XSD.dateTime),
        )
    )

    optional_values = (
        (CITY.temperatureCelsius, observation.temperature_c),
        (CITY.relativeHumidityPercent, observation.relative_humidity_pct),
        (CITY.pressureHpa, observation.pressure_hpa),
        (CITY.windSpeedKmh, observation.wind_speed_kmh),
    )
    for predicate, value in optional_values:
        if value is not None:
            graph.add((subject, predicate, Literal(value, datatype=XSD.double)))

    if observation.condition:
        graph.add((subject, CITY.weatherCondition, Literal(observation.condition)))

    return graph
