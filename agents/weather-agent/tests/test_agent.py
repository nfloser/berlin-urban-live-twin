"""Tests for the weather ingestion agent."""

from unittest.mock import Mock

from app.agent import WeatherAgent


def test_refresh_returns_semantic_weather_graph() -> None:
    client = Mock()
    client.get_current_weather.return_value = {
        "weather": {
            "timestamp": "2026-09-14T08:00:00+00:00",
            "temperature": 18.2,
            "relative_humidity": 63,
            "pressure_msl": 1017.4,
            "wind_speed": 11.5,
            "condition": "dry",
        }
    }

    graph = WeatherAgent(client=client).refresh()

    assert len(graph) >= 2
