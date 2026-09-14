"""Tests for the air-quality ingestion workflow."""

from unittest.mock import Mock

from app.agent import AirQualityAgent


def test_refresh_stations_ingests_only_valid_station_payloads() -> None:
    client = Mock()
    client.get_stations.return_value = [
        {
            "name": "010 Wedding",
            "code": "mc010",
            "lat": "52.54291",
            "lng": "13.34926",
            "active": True,
            "stationgroups": ["background"],
        },
        {
            "name": "broken",
            "lat": "not-a-number",
            "lng": "13.4",
        },
    ]

    agent = AirQualityAgent(client=client)

    result = agent.refresh_stations()

    assert result.ingested == 1
    assert result.rejected == 1
    assert agent.knowledge_graph.active_station_codes() == ["MC010"]
