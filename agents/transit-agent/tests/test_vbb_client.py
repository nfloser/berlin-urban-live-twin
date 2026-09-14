"""Tests for the official VBB GTFS-Realtime client."""

from unittest.mock import Mock

from app.vbb_client import VbbRealtimeClient


def test_fetch_uses_official_feed_and_identifying_user_agent() -> None:
    session = Mock()
    response = Mock()
    response.content = b"gtfs-rt"
    session.get.return_value = response

    client = VbbRealtimeClient(session=session)
    payload = client.fetch()

    session.get.assert_called_once_with(
        "https://production.gtfsrt.vbb.de/data",
        headers={
            "User-Agent": "berlin-urban-live-twin/0.1 (+https://github.com/nfloser/berlin-urban-live-twin)"
        },
        timeout=15,
    )
    response.raise_for_status.assert_called_once_with()
    assert payload == b"gtfs-rt"
