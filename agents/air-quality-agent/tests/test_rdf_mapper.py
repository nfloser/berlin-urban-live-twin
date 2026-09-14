"""Tests for RDF conversion of air-quality domain objects."""

from datetime import datetime

from rdflib import RDF, XSD, Literal, Namespace, URIRef

from app.models import AirQualityIndexObservation, AirQualityStation
from app.rdf_mapper import CITY, GEO, lqi_to_graph, station_to_graph

PROV = Namespace("http://www.w3.org/ns/prov#")
BERLIN_LQI_SOURCE = URIRef("https://luftdaten.berlin.de/api/lqis/data")


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


def test_lqi_to_graph_links_observation_to_station_components_and_source() -> None:
    observation = AirQualityIndexObservation(
        station_code="MC010",
        observed_at=datetime.fromisoformat("2026-09-14T08:00:00+00:00"),
        grade=3,
        component_grades={"PM10": 2, "O3": 3},
    )

    graph = lqi_to_graph(observation)
    subject = URIRef("https://example.org/berlin/lqi/MC010/20260914T080000Z")
    station = URIRef("https://example.org/berlin/station/MC010")

    assert (subject, RDF.type, CITY.AirQualityIndexObservation) in graph
    assert (subject, CITY.observedAt, Literal("2026-09-14T08:00:00+00:00", datatype=XSD.dateTime)) in graph
    assert (subject, CITY.airQualityGrade, Literal(3, datatype=XSD.integer)) in graph
    assert (subject, CITY.observedAtStation, station) in graph
    assert (subject, CITY.lqiPM10, Literal(2, datatype=XSD.integer)) in graph
    assert (subject, CITY.lqiO3, Literal(3, datatype=XSD.integer)) in graph
    assert (subject, PROV.wasDerivedFrom, BERLIN_LQI_SOURCE) in graph
