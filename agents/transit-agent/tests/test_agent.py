"""Tests for the transit ingestion workflow."""

from unittest.mock import Mock

from google.transit import gtfs_realtime_pb2

from app.agent import TransitAgent


def test_refresh_returns_semantic_transit_graph() -> None:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1_789_375_200
    entity = feed.entity.add()
    entity.id = "trip"
    entity.trip_update.trip.trip_id = "trip-1"
    update = entity.trip_update.stop_time_update.add()
    update.arrival.delay = 120

    client = Mock()
    client.fetch.return_value = feed.SerializeToString()

    graph = TransitAgent(client=client).refresh()

    assert len(graph) >= 2
