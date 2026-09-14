"""Repository abstraction for the persisted RDF representation of the twin."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rdflib import Graph


class TwinRepository:
    """Load and query Turtle files produced by domain agents."""

    def __init__(self, data_directory: Path) -> None:
        self._data_directory = data_directory
        self.graph = Graph()

    def reload(self) -> None:
        """Rebuild the in-memory graph from all Turtle files in the data directory."""
        graph = Graph()
        if self._data_directory.exists():
            for path in sorted(self._data_directory.glob("*.ttl")):
                graph.parse(path, format="turtle")
        self.graph = graph

    def active_station_count(self) -> int:
        """Return the number of active air-quality stations in the graph."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        SELECT (COUNT(?station) AS ?count)
        WHERE {
            ?station a city:AirQualityStation ;
                     city:isActive true .
        }
        """
        row = next(iter(self.graph.query(query)), None)
        return int(row[0]) if row is not None else 0

    def active_stations(self) -> list[dict[str, Any]]:
        """Return active stations in a map-friendly representation."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

        SELECT ?code ?name ?lat ?lon
        WHERE {
            ?station a city:AirQualityStation ;
                     city:stationCode ?code ;
                     city:name ?name ;
                     city:isActive true ;
                     geo:lat ?lat ;
                     geo:long ?lon .
        }
        ORDER BY ?code
        """
        return [
            {
                "code": str(row.code),
                "name": str(row.name),
                "latitude": float(row.lat),
                "longitude": float(row.lon),
            }
            for row in self.graph.query(query)
        ]

    def latest_weather(self) -> dict[str, Any] | None:
        """Return the latest weather observation stored in the graph."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>

        SELECT ?observedAt ?temperature ?humidity
        WHERE {
            ?observation a city:WeatherObservation ;
                         city:observedAt ?observedAt .
            OPTIONAL { ?observation city:temperatureCelsius ?temperature . }
            OPTIONAL { ?observation city:relativeHumidityPercent ?humidity . }
        }
        ORDER BY DESC(?observedAt)
        LIMIT 1
        """
        row = next(iter(self.graph.query(query)), None)
        if row is None:
            return None
        return {
            "observed_at": str(row.observedAt),
            "temperature_c": float(row.temperature) if row.temperature is not None else None,
            "relative_humidity_pct": float(row.humidity) if row.humidity is not None else None,
        }

    def latest_transit(self) -> dict[str, Any] | None:
        """Return the latest aggregated VBB realtime observation."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>

        SELECT ?observedAt ?total ?delayed ?maxDelay ?delayedShare
        WHERE {
            ?observation a city:TransitObservation ;
                         city:observedAt ?observedAt ;
                         city:totalTripUpdates ?total ;
                         city:delayedTripUpdates ?delayed ;
                         city:maxDelaySeconds ?maxDelay ;
                         city:delayedShare ?delayedShare .
        }
        ORDER BY DESC(?observedAt)
        LIMIT 1
        """
        row = next(iter(self.graph.query(query)), None)
        if row is None:
            return None
        return {
            "observed_at": str(row.observedAt),
            "total_trip_updates": int(row.total),
            "delayed_trip_updates": int(row.delayed),
            "max_delay_seconds": int(row.maxDelay),
            "delayed_share": float(row.delayedShare),
        }
