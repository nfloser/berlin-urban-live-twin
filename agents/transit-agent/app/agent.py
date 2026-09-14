"""Application service for VBB realtime ingestion."""

from rdflib import Graph

from app.gtfs_parser import parse_transit_snapshot
from app.rdf_mapper import transit_to_graph
from app.vbb_client import VbbRealtimeClient


class TransitAgent:
    """Retrieve VBB realtime data and produce its semantic representation."""

    def __init__(self, client: VbbRealtimeClient | None = None) -> None:
        self._client = client or VbbRealtimeClient()

    def refresh(self) -> Graph:
        """Fetch, summarise, and map the current GTFS-Realtime feed."""
        payload = self._client.fetch()
        snapshot = parse_transit_snapshot(payload)
        return transit_to_graph(snapshot)
