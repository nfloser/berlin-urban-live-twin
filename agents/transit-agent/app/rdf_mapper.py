"""RDF mapping for aggregated VBB realtime observations."""

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.models import TransitSnapshot

CITY = Namespace("https://example.org/berlin/ontology/")
PROV = Namespace("http://www.w3.org/ns/prov#")
TRANSIT_BASE = "https://example.org/berlin/transit/"
VBB_SOURCE = URIRef("https://production.gtfsrt.vbb.de/data")


def transit_to_graph(snapshot: TransitSnapshot) -> Graph:
    graph = Graph()
    graph.bind("city", CITY)
    graph.bind("prov", PROV)
    subject = URIRef(f"{TRANSIT_BASE}{snapshot.generated_at.isoformat()}")
    graph.add((subject, RDF.type, CITY.TransitObservation))
    graph.add((subject, CITY.observedAt, Literal(snapshot.generated_at.isoformat(), datatype=XSD.dateTime)))
    graph.add((subject, PROV.wasDerivedFrom, VBB_SOURCE))
    graph.add((subject, CITY.totalTripUpdates, Literal(snapshot.total_trip_updates, datatype=XSD.integer)))
    graph.add((subject, CITY.delayedTripUpdates, Literal(snapshot.delayed_trip_updates, datatype=XSD.integer)))
    graph.add((subject, CITY.maxDelaySeconds, Literal(snapshot.max_delay_seconds, datatype=XSD.integer)))
    graph.add((subject, CITY.delayedShare, Literal(snapshot.delayed_share, datatype=XSD.double)))
    return graph
