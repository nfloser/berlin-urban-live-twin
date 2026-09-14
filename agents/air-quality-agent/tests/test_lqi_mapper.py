"""Tests for mapping official Berlin LQI payloads."""

from app.lqi_mapper import map_lqi_observation


def test_maps_official_lqi_observation() -> None:
    payload = {
        "station": "MC010",
        "timestamp": "2026-09-14T08:00:00+00:00",
        "lqi": 3,
        "pm10": 2,
        "pm25": 1,
        "no2": 1,
        "o3": 3,
        "co": None,
    }

    observation = map_lqi_observation(payload)

    assert observation.station_code == "MC010"
    assert observation.grade == 3
    assert observation.component_grades == {
        "PM10": 2,
        "PM2.5": 1,
        "NO2": 1,
        "O3": 3,
    }
    assert observation.observed_at.isoformat() == "2026-09-14T08:00:00+00:00"


def test_mapper_accepts_nested_station_code_and_index_alias() -> None:
    payload = {
        "station": {"code": "mc174"},
        "date": "2026-09-14T09:00:00+02:00",
        "index": "4",
        "components": {"PM10": 3, "PM2.5": 2, "NO2": 4},
    }

    observation = map_lqi_observation(payload)

    assert observation.station_code == "MC174"
    assert observation.grade == 4
    assert observation.component_grades["NO2"] == 4
