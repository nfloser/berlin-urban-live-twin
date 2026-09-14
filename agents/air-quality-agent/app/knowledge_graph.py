"""Local knowledge-graph abstraction used during the early project stages."""

from __future__ import annotations

from rdflib import Graph


class LocalKnowledgeGraph:
    """In-memory RDF graph with a small SPARQL-oriented query API."""

    def __init__(self) -> None:
        self._graph = Graph()

    @property
    def graph(self) -> Graph:
        """Expose the underlying RDFLib graph for serialization and inspection."""
        return self._graph

    def merge(self, graph: Graph) -> None:
        """Merge triples from another graph into the local knowledge graph."""
        for triple in graph:
            self._graph.add(triple)

    def active_station_codes(self) -> list[str]:
        """Return station codes for stations marked as active using SPARQL."""
        query = """
        PREFIX city: <https://example.org/berlin/ontology/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?code
        WHERE {
            ?station a city:AirQualityStation ;
                     city:stationCode ?code ;
                     city:isActive true .
        }
        ORDER BY ?code
        """
        return [str(row.code) for row in self._graph.query(query)]
