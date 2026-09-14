"""Tests for mapping Berlin station payloads into domain objects."""

from app.station_mapper import map_station


def test_map_station_converts_coordinates_and_normalises_code() -> None:
    payload = {
        "name": "010 Wedding",
        "code": "mc010",
        "address": "13353 Berlin, Amrumer Str./Limburger Str.",
        "lat": "52.54291000",
        "lng": "13.34926000",
        "active": True,
        "stationgroups": ["background"],
    }

    station = map_station(payload)

    assert station.code == "MC010"
    assert station.name == "010 Wedding"
    assert station.latitude == 52.54291
    assert station.longitude == 13.34926
    assert station.active is True
    assert station.categories == ("background",)


def test_map_station_rejects_missing_code() -> None:
    payload = {
        "name": "Invalid station",
        "lat": "52.5",
        "lng": "13.4",
    }

    try:
        map_station(payload)
    except ValueError as exc:
        assert "code" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
