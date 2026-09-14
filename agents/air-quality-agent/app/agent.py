"""Application service for ingesting Berlin air-quality station data."""

from __future__ import annotations

from dataclasses import dataclass

from app.berlin_api import BerlinAirQualityClient
from app.knowledge_graph import LocalKnowledgeGraph
from app.rdf_mapper import station_to_graph
from app.station_mapper import map_station


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Summary of one ingestion cycle."""

    ingested: int
    rejected: int


class AirQualityAgent:
    """Retrieve station data, normalise it, and update the knowledge graph."""

    def __init__(
        self,
        client: BerlinAirQualityClient | None = None,
        knowledge_graph: LocalKnowledgeGraph | None = None,
    ) -> None:
        self._client = client or BerlinAirQualityClient()
        self.knowledge_graph = knowledge_graph or LocalKnowledgeGraph()

    def refresh_stations(self) -> IngestionResult:
        """Fetch station metadata and merge valid stations into the graph."""
        ingested = 0
        rejected = 0

        for payload in self._client.get_stations():
            try:
                station = map_station(payload)
            except (TypeError, ValueError):
                rejected += 1
                continue

            self.knowledge_graph.merge(station_to_graph(station))
            ingested += 1

        return IngestionResult(ingested=ingested, rejected=rejected)
