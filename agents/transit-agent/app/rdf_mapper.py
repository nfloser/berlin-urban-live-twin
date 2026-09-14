"""RDF mapping for aggregated VBB realtime observations."""

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.models import TransitSnapshot

CITY = Namespace("https://example.org/berlin/ontology/")
TRANSIT_BASE = "https://example.org/berlin/transit/"


def transit_to_graph(snapshot: TransitSnapshot) -> Graph:
    """Create an RDF graph for one transit realtime snapshot."""
    graph = Graph()
    graph.bind("city", CITY)

    subject = URIRef(f"{TRANSIT_BASE}{snapshot.generated_at.isoformat()}")
    graph.add((subject, RDF.type, CITY.TransitObservation))
    graph.add(
        (
            subject,
            CITY.observedAt,
            Literal(snapshot.generated_at.isoformat(), datatype=XSD.dateTime),
        )
    )
    graph.add(
        (
            subject,
            CITY.totalTripUpdates,
            Literal(snapshot.total_trip_updates, datatype=XSD.integer),
        )
    )
    graph.add(
        (
            subject,
            CITY.delayedTripUpdates,
            Literal(snapshot.delayed_trip_updates, datatype=XSD.integer),
        )
    )
    graph.add(
        (
            subject,
            CITY.maxDelaySeconds,
            Literal(snapshot.max_delay_seconds, datatype=XSD.integer),
        )
    )
    graph.add(
        (
            subject,
            CITY.delayedShare,
            Literal(snapshot.delayed_share, datatype=XSD.double),
        )
    )
    return graph
