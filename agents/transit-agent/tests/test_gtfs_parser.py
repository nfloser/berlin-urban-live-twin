"""Tests for summarising VBB GTFS-Realtime trip updates."""

from google.transit import gtfs_realtime_pb2

from app.gtfs_parser import parse_transit_snapshot


def test_parse_transit_snapshot_counts_delayed_trip_updates() -> None:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 1_789_375_200

    delayed = feed.entity.add()
    delayed.id = "delayed"
    delayed.trip_update.trip.trip_id = "trip-1"
    delayed_update = delayed.trip_update.stop_time_update.add()
    delayed_update.arrival.delay = 180

    on_time = feed.entity.add()
    on_time.id = "on-time"
    on_time.trip_update.trip.trip_id = "trip-2"
    on_time_update = on_time.trip_update.stop_time_update.add()
    on_time_update.arrival.delay = 30

    snapshot = parse_transit_snapshot(feed.SerializeToString())

    assert snapshot.total_trip_updates == 2
    assert snapshot.delayed_trip_updates == 1
    assert snapshot.max_delay_seconds == 180
    assert snapshot.delayed_share == 0.5
