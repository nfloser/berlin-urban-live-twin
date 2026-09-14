"""Tests for semantic representation of transit summaries."""

from datetime import datetime, timezone

from rdflib import RDF, XSD, Literal, Namespace, URIRef

from app.models import TransitSnapshot
from app.rdf_mapper import CITY, transit_to_graph

PROV = Namespace("http://www.w3.org/ns/prov#")


def test_transit_snapshot_to_graph_creates_summary_triples_and_lineage() -> None:
    snapshot = TransitSnapshot(
        generated_at=datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc),
        total_trip_updates=200,
        delayed_trip_updates=40,
        max_delay_seconds=420,
    )

    graph = transit_to_graph(snapshot)
    subject = URIRef("https://example.org/berlin/transit/2026-09-14T08:00:00+00:00")

    assert (subject, RDF.type, CITY.TransitObservation) in graph
    assert (subject, CITY.totalTripUpdates, Literal(200, datatype=XSD.integer)) in graph
    assert (subject, CITY.delayedTripUpdates, Literal(40, datatype=XSD.integer)) in graph
    assert (subject, CITY.delayedShare, Literal(0.2, datatype=XSD.double)) in graph
    assert (subject, PROV.wasDerivedFrom, URIRef("https://production.gtfsrt.vbb.de/data")) in graph
