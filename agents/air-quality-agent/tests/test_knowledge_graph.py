"""Tests for the local RDF knowledge graph abstraction."""

from app.knowledge_graph import LocalKnowledgeGraph
from app.models import AirQualityStation
from app.rdf_mapper import station_to_graph


def test_graph_can_query_active_station_codes() -> None:
    station = AirQualityStation(
        code="MC010",
        name="010 Wedding",
        latitude=52.54291,
        longitude=13.34926,
        address=None,
        active=True,
        categories=("background",),
    )
    knowledge_graph = LocalKnowledgeGraph()
    knowledge_graph.merge(station_to_graph(station))

    assert knowledge_graph.active_station_codes() == ["MC010"]


def test_graph_does_not_return_inactive_stations_as_active() -> None:
    station = AirQualityStation(
        code="MC018",
        name="018 Schöneberg",
        latitude=52.48579,
        longitude=13.34885,
        address=None,
        active=False,
        categories=("background",),
    )
    knowledge_graph = LocalKnowledgeGraph()
    knowledge_graph.merge(station_to_graph(station))

    assert knowledge_graph.active_station_codes() == []
