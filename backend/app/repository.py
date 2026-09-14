"""Repository abstraction for the persisted RDF representation of the twin."""

from __future__ import annotations

from pathlib import Path

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
        return int(row.count) if row is not None else 0
