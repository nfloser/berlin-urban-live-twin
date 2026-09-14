"""RDF mapping for air-quality domain objects."""

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.models import AirQualityStation

CITY = Namespace("https://example.org/berlin/ontology/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
STATION_BASE = "https://example.org/berlin/station/"


def station_to_graph(station: AirQualityStation) -> Graph:
    """Create an RDF graph describing one monitoring station."""
    graph = Graph()
    graph.bind("city", CITY)
    graph.bind("geo", GEO)

    subject = URIRef(f"{STATION_BASE}{station.code}")
    graph.add((subject, RDF.type, CITY.AirQualityStation))
    graph.add((subject, CITY.stationCode, Literal(station.code)))
    graph.add((subject, CITY.name, Literal(station.name)))
    graph.add((subject, GEO.lat, Literal(station.latitude, datatype=XSD.double)))
    graph.add((subject, GEO.long, Literal(station.longitude, datatype=XSD.double)))
    graph.add((subject, CITY.isActive, Literal(station.active, datatype=XSD.boolean)))

    if station.address:
        graph.add((subject, CITY.address, Literal(station.address)))

    for category in station.categories:
        graph.add((subject, CITY.stationCategory, Literal(category)))

    return graph
