"""GTFS-Realtime parsing helpers for VBB trip updates."""

from __future__ import annotations

from datetime import datetime, timezone

from google.transit import gtfs_realtime_pb2

from app.models import TransitSnapshot

DELAY_THRESHOLD_SECONDS = 60


def parse_transit_snapshot(payload: bytes) -> TransitSnapshot:
    """Summarise trip-update delays from a GTFS-Realtime payload."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(payload)

    total_trip_updates = 0
    delayed_trip_updates = 0
    max_delay_seconds = 0

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        total_trip_updates += 1
        trip_max_delay = 0

        for stop_update in entity.trip_update.stop_time_update:
            delays: list[int] = []
            if stop_update.HasField("arrival") and stop_update.arrival.HasField("delay"):
                delays.append(stop_update.arrival.delay)
            if stop_update.HasField("departure") and stop_update.departure.HasField("delay"):
                delays.append(stop_update.departure.delay)
            if delays:
                trip_max_delay = max(trip_max_delay, max(delays))

        max_delay_seconds = max(max_delay_seconds, trip_max_delay)
        if trip_max_delay > DELAY_THRESHOLD_SECONDS:
            delayed_trip_updates += 1

    generated_at = datetime.fromtimestamp(feed.header.timestamp, tz=timezone.utc)

    return TransitSnapshot(
        generated_at=generated_at,
        total_trip_updates=total_trip_updates,
        delayed_trip_updates=delayed_trip_updates,
        max_delay_seconds=max_delay_seconds,
    )
