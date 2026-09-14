"""RDF mapping for derived urban-stress observations."""

from datetime import datetime

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.urban_stress import UrbanStressResult

CITY = Namespace("https://example.org/berlin/ontology/")
DERIVED_BASE = "https://example.org/berlin/derived/urban-stress/"


def urban_stress_to_graph(result: UrbanStressResult, observed_at: datetime) -> Graph:
    """Create RDF triples for a derived urban-stress observation."""
    graph = Graph()
    graph.bind("city", CITY)

    subject = URIRef(f"{DERIVED_BASE}{observed_at.isoformat()}")
    graph.add((subject, RDF.type, CITY.UrbanStressObservation))
    graph.add((subject, CITY.observedAt, Literal(observed_at.isoformat(), datatype=XSD.dateTime)))
    graph.add((subject, CITY.urbanStressIndex, Literal(result.index, datatype=XSD.double)))
    graph.add(
        (
            subject,
            CITY.airQualityStressComponent,
            Literal(result.air_quality_component, datatype=XSD.double),
        )
    )
    graph.add((subject, CITY.heatStressComponent, Literal(result.heat_component, datatype=XSD.double)))
    graph.add(
        (
            subject,
            CITY.transitStressComponent,
            Literal(result.transit_component, datatype=XSD.double),
        )
    )
    return graph
