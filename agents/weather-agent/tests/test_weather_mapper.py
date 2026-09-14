"""Tests for normalising current weather observations."""

from datetime import datetime

from app.weather_mapper import map_current_weather


def test_map_current_weather_converts_bright_sky_payload() -> None:
    payload = {
        "weather": {
            "timestamp": "2026-09-14T08:00:00+00:00",
            "temperature": 18.2,
            "relative_humidity": 63,
            "pressure_msl": 1017.4,
            "wind_speed": 11.5,
            "condition": "dry",
        }
    }

    observation = map_current_weather(payload)

    assert observation.observed_at == datetime.fromisoformat("2026-09-14T08:00:00+00:00")
    assert observation.temperature_c == 18.2
    assert observation.relative_humidity_pct == 63.0
    assert observation.pressure_hpa == 1017.4
    assert observation.wind_speed_kmh == 11.5
    assert observation.condition == "dry"


def test_map_current_weather_rejects_missing_weather_object() -> None:
    try:
        map_current_weather({})
    except ValueError as exc:
        assert "weather" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
