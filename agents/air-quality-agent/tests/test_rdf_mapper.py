"""Tests for RDF conversion of air-quality domain objects."""

from rdflib import RDF, XSD, Literal, URIRef

from app.models import AirQualityStation
from app.rdf_mapper import CITY, GEO, station_to_graph


def test_station_to_graph_creates_semantic_station_representation() -> None:
    station = AirQualityStation(
        code="MC010",
        name="010 Wedding",
        latitude=52.54291,
        longitude=13.34926,
        address="13353 Berlin, Amrumer Str./Limburger Str.",
        active=True,
        categories=("background",),
    )

    graph = station_to_graph(station)
    subject = URIRef("https://example.org/berlin/station/MC010")

    assert (subject, RDF.type, CITY.AirQualityStation) in graph
    assert (subject, CITY.stationCode, Literal("MC010")) in graph
    assert (subject, GEO.lat, Literal(52.54291, datatype=XSD.double)) in graph
    assert (subject, GEO.long, Literal(13.34926, datatype=XSD.double)) in graph
    assert (subject, CITY.isActive, Literal(True, datatype=XSD.boolean)) in graph
