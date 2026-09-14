"""Repository abstraction for querying the semantic twin state."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore


def create_remote_graph(sparql_endpoint_url: str) -> Graph:
    """Create an RDFLib graph whose queries execute directly against SPARQL."""
    store = SPARQLStore(query_endpoint=sparql_endpoint_url)
    return Graph(store=store)


class TwinRepository:
    """Query twin state from SPARQL, Graph Store, or local Turtle files."""

    def __init__(
        self,
        data_directory: Path,
        *,
        sparql_endpoint_url: str | None = None,
        graph_store_url: str | None = None,
        session: requests.Session | None = None,
        timeout: int = 10,
    ) -> None:
        self._data_directory = data_directory
        self._sparql_endpoint_url = sparql_endpoint_url
        self._graph_store_url = graph_store_url
        self._session = session or requests.Session()
        self._timeout = timeout
        self.graph = Graph()

    def reload(self) -> None:
        """Recreate the repository graph from the configured state source."""
        if self._sparql_endpoint_url:
            self.graph = create_remote_graph(self._sparql_endpoint_url)
            return

        graph = Graph()
        if self._graph_store_url:
            response = self._session.get(
                self._graph_store_url,
                headers={"Accept": "text/turtle"},
                timeout=self._timeout,
            )
            response.raise_for_status()
            graph.parse(data=response.text, format="turtle")
        elif self._data_directory.exists():
            for path in sorted(self._data_directory.glob("*.ttl")):
                graph.parse(path, format="turtle")
        self.graph = graph

    def active_station_count(self) -> int:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT (COUNT(?station) AS ?count)
        WHERE { ?station a city:AirQualityStation ; city:isActive true . }
        """
        row = next(iter(self.graph.query(query)), None)
        return int(row[0]) if row is not None else 0

    def triple_count(self) -> int:
        query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o . }"
        row = next(iter(self.graph.query(query)), None)
        return int(row[0]) if row is not None else 0

    def active_stations(self) -> list[dict[str, Any]]:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
        SELECT ?code ?name ?lat ?lon
        WHERE {
            ?station a city:AirQualityStation ; city:stationCode ?code ; city:name ?name ;
                     city:isActive true ; geo:lat ?lat ; geo:long ?lon .
        }
        ORDER BY ?code
        """
        return [{"code": str(r.code), "name": str(r.name), "latitude": float(r.lat), "longitude": float(r.lon)} for r in self.graph.query(query)]

    def latest_air_quality(self) -> dict[str, Any] | None:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT ?stationCode ?observedAt ?grade ?pm10 ?pm25 ?no2 ?o3 ?co ?so2
        WHERE {
            ?obs a city:AirQualityIndexObservation ; city:observedAt ?observedAt ;
                 city:airQualityGrade ?grade ; city:observedAtStation ?station .
            ?station city:stationCode ?stationCode .
            OPTIONAL { ?obs city:lqiPM10 ?pm10 . }
            OPTIONAL { ?obs city:lqiPM25 ?pm25 . }
            OPTIONAL { ?obs city:lqiNO2 ?no2 . }
            OPTIONAL { ?obs city:lqiO3 ?o3 . }
            OPTIONAL { ?obs city:lqiCO ?co . }
            OPTIONAL { ?obs city:lqiSO2 ?so2 . }
        }
        ORDER BY DESC(?observedAt) ?stationCode
        """
        rows = list(self.graph.query(query))
        if not rows:
            return None
        newest = str(rows[0].observedAt)
        current = [r for r in rows if str(r.observedAt) == newest]
        stations = []
        for r in current:
            components = {}
            for key, value in (("PM10", r.pm10), ("PM2.5", r.pm25), ("NO2", r.no2), ("O3", r.o3), ("CO", r.co), ("SO2", r.so2)):
                if value is not None:
                    components[key] = int(value)
            stations.append({"station_code": str(r.stationCode), "grade": int(r.grade), "components": components})
        return {"observed_at": newest, "worst_grade": max(item["grade"] for item in stations), "stations": stations}

    def latest_weather(self) -> dict[str, Any] | None:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT ?observedAt ?temperature ?humidity WHERE {
            ?observation a city:WeatherObservation ; city:observedAt ?observedAt .
            OPTIONAL { ?observation city:temperatureCelsius ?temperature . }
            OPTIONAL { ?observation city:relativeHumidityPercent ?humidity . }
        } ORDER BY DESC(?observedAt) LIMIT 1
        """
        row = next(iter(self.graph.query(query)), None)
        if row is None:
            return None
        return {"observed_at": str(row.observedAt), "temperature_c": float(row.temperature) if row.temperature is not None else None, "relative_humidity_pct": float(row.humidity) if row.humidity is not None else None}

    def latest_transit(self) -> dict[str, Any] | None:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT ?observedAt ?total ?delayed ?maxDelay ?delayedShare WHERE {
            ?observation a city:TransitObservation ; city:observedAt ?observedAt ;
                         city:totalTripUpdates ?total ; city:delayedTripUpdates ?delayed ;
                         city:maxDelaySeconds ?maxDelay ; city:delayedShare ?delayedShare .
        } ORDER BY DESC(?observedAt) LIMIT 1
        """
        row = next(iter(self.graph.query(query)), None)
        if row is None:
            return None
        return {"observed_at": str(row.observedAt), "total_trip_updates": int(row.total), "delayed_trip_updates": int(row.delayed), "max_delay_seconds": int(row.maxDelay), "delayed_share": float(row.delayedShare)}

    def latest_urban_stress(self) -> dict[str, Any] | None:
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT ?observedAt ?stressIndex ?air ?heat ?transit WHERE {
            ?observation a city:UrbanStressObservation ; city:observedAt ?observedAt ;
                         city:urbanStressIndex ?stressIndex ; city:airQualityStressComponent ?air ;
                         city:heatStressComponent ?heat ; city:transitStressComponent ?transit .
        } ORDER BY DESC(?observedAt) LIMIT 1
        """
        row = next(iter(self.graph.query(query)), None)
        if row is None:
            return None
        return {
            "observed_at": str(row[0]),
            "index": float(row[1]),
            "air_quality_component": float(row[2]),
            "heat_component": float(row[3]),
            "transit_component": float(row[4]),
        }

    def provenance_summary(self) -> list[dict[str, Any]]:
        """Summarise observation lineage recorded with PROV-O."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?type ?source (COUNT(?observation) AS ?count)
        WHERE {
            ?observation a ?type ; prov:wasDerivedFrom ?source .
            VALUES ?type {
                city:AirQualityIndexObservation
                city:WeatherObservation
                city:TransitObservation
                city:UrbanStressObservation
            }
        }
        GROUP BY ?type ?source
        ORDER BY ?type ?source
        """
        rows = []
        for row in self.graph.query(query):
            type_name = str(row[0]).rsplit("/", 1)[-1]
            rows.append({"observation_type": type_name, "source": str(row[1]), "count": int(row[2])})
        return rows

    def latest_observation_timestamps(self) -> dict[str, datetime | None]:
        classes = {
            "air_quality": "AirQualityIndexObservation",
            "weather": "WeatherObservation",
            "transit": "TransitObservation",
            "urban_stress": "UrbanStressObservation",
        }
        result: dict[str, datetime | None] = {}
        for source, class_name in classes.items():
            query = f"""
            PREFIX city: <https://example.org/berlin/ontology/>
            SELECT ?observedAt WHERE {{
                ?observation a city:{class_name} ; city:observedAt ?observedAt .
            }} ORDER BY DESC(?observedAt) LIMIT 1
            """
            row = next(iter(self.graph.query(query)), None)
            result[source] = (
                datetime.fromisoformat(str(row[0]).replace("Z", "+00:00"))
                if row is not None
                else None
            )
        return result
