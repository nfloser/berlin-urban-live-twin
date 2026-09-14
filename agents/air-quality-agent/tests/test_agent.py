"""Tests for the air-quality ingestion workflow."""

from unittest.mock import Mock

from rdflib import RDF

from app.agent import AirQualityAgent
from app.rdf_mapper import CITY


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


def test_refresh_lqi_ingests_valid_official_index_records() -> None:
    client = Mock()
    client.get_lqi_data.return_value = {
        "data": [
            {
                "station": "MC010",
                "timestamp": "2026-09-14T08:00:00+00:00",
                "lqi": 3,
                "pm10": 2,
                "o3": 3,
            },
            {"station": "MC174", "timestamp": "broken", "lqi": 2},
        ]
    }
    agent = AirQualityAgent(client=client)

    result = agent.refresh_lqi()

    assert result.ingested == 1
    assert result.rejected == 1
    observations = list(
        agent.knowledge_graph.graph.subjects(RDF.type, CITY.AirQualityIndexObservation)
    )
    assert len(observations) == 1
