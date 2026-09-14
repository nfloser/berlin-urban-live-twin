"""Tests for semantic representation of derived urban-stress values."""

from datetime import datetime, timezone

from rdflib import RDF, XSD, Literal, Namespace, URIRef

from app.rdf_mapper import CITY, urban_stress_to_graph
from app.urban_stress import UrbanStressResult

PROV = Namespace("http://www.w3.org/ns/prov#")


def test_urban_stress_to_graph_records_components_and_lineage() -> None:
    result = UrbanStressResult(
        air_quality_component=0.6,
        heat_component=0.5,
        transit_component=0.4,
        index=52.0,
    )
    observed_at = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)

    graph = urban_stress_to_graph(result, observed_at)
    subject = URIRef("https://example.org/berlin/derived/urban-stress/2026-09-14T08:00:00+00:00")

    assert (subject, RDF.type, CITY.UrbanStressObservation) in graph
    assert (subject, CITY.urbanStressIndex, Literal(52.0, datatype=XSD.double)) in graph
    assert (subject, CITY.airQualityStressComponent, Literal(0.6, datatype=XSD.double)) in graph

    sources = set(graph.objects(subject, PROV.wasDerivedFrom))
    assert sources == {
        URIRef("https://luftdaten.berlin.de/api/lqis/data"),
        URIRef("https://api.brightsky.dev/current_weather"),
        URIRef("https://production.gtfsrt.vbb.de/data"),
    }
