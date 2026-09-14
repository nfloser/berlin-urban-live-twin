"""RDF mapping for derived urban-stress observations."""

from datetime import datetime

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.urban_stress import UrbanStressResult

CITY = Namespace("https://example.org/berlin/ontology/")
PROV = Namespace("http://www.w3.org/ns/prov#")
DERIVED_BASE = "https://example.org/berlin/derived/urban-stress/"
BERLIN_LQI_SOURCE = URIRef("https://luftdaten.berlin.de/api/lqis/data")
WEATHER_SOURCE = URIRef("https://api.brightsky.dev/current_weather")
VBB_SOURCE = URIRef("https://production.gtfsrt.vbb.de/data")


def urban_stress_to_graph(result: UrbanStressResult, observed_at: datetime) -> Graph:
    graph = Graph()
    graph.bind("city", CITY)
    graph.bind("prov", PROV)
    subject = URIRef(f"{DERIVED_BASE}{observed_at.isoformat()}")
    graph.add((subject, RDF.type, CITY.UrbanStressObservation))
    graph.add((subject, CITY.observedAt, Literal(observed_at.isoformat(), datatype=XSD.dateTime)))
    graph.add((subject, CITY.urbanStressIndex, Literal(result.index, datatype=XSD.double)))
    graph.add((subject, CITY.airQualityStressComponent, Literal(result.air_quality_component, datatype=XSD.double)))
    graph.add((subject, CITY.heatStressComponent, Literal(result.heat_component, datatype=XSD.double)))
    graph.add((subject, CITY.transitStressComponent, Literal(result.transit_component, datatype=XSD.double)))
    for source in (BERLIN_LQI_SOURCE, WEATHER_SOURCE, VBB_SOURCE):
        graph.add((subject, PROV.wasDerivedFrom, source))
    return graph
