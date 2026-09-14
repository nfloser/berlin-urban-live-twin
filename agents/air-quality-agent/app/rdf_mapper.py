"""RDF mapping for air-quality domain objects."""

from datetime import timezone

from rdflib import RDF, XSD, Graph, Literal, Namespace, URIRef

from app.models import AirQualityIndexObservation, AirQualityStation

CITY = Namespace("https://example.org/berlin/ontology/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
STATION_BASE = "https://example.org/berlin/station/"
LQI_BASE = "https://example.org/berlin/lqi/"


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


def lqi_to_graph(observation: AirQualityIndexObservation) -> Graph:
    """Create RDF for one official Berlin LQI observation."""
    graph = Graph()
    graph.bind("city", CITY)

    observed_utc = observation.observed_at.astimezone(timezone.utc)
    timestamp_id = observed_utc.strftime("%Y%m%dT%H%M%SZ")
    subject = URIRef(f"{LQI_BASE}{observation.station_code}/{timestamp_id}")
    station = URIRef(f"{STATION_BASE}{observation.station_code}")

    graph.add((subject, RDF.type, CITY.AirQualityIndexObservation))
    graph.add((subject, CITY.observedAtStation, station))
    graph.add((subject, CITY.observedAt, Literal(observation.observed_at.isoformat(), datatype=XSD.dateTime)))
    graph.add((subject, CITY.airQualityGrade, Literal(observation.grade, datatype=XSD.integer)))

    predicates = {
        "PM10": CITY.lqiPM10,
        "PM2.5": CITY.lqiPM25,
        "NO2": CITY.lqiNO2,
        "O3": CITY.lqiO3,
        "CO": CITY.lqiCO,
        "SO2": CITY.lqiSO2,
    }
    for component, grade in observation.component_grades.items():
        predicate = predicates.get(component)
        if predicate is not None:
            graph.add((subject, predicate, Literal(grade, datatype=XSD.integer)))

    return graph
