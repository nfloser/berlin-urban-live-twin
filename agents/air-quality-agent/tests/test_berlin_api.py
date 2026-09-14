"""Tests for the Berlin air quality API client."""

from unittest.mock import Mock

import pytest

from app.berlin_api import BerlinAirQualityClient


@pytest.fixture
def session() -> Mock:
    """Return a mocked HTTP session."""
    return Mock()


def test_get_stations_requests_official_stations_endpoint(session: Mock) -> None:
    response = Mock()
    response.json.return_value = [{"code": "MC010", "name": "Wedding"}]
    session.get.return_value = response

    client = BerlinAirQualityClient(session=session)
    stations = client.get_stations()

    session.get.assert_called_once_with(
        "https://luftdaten.berlin.de/api/stations",
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    assert stations == [{"code": "MC010", "name": "Wedding"}]


def test_get_station_data_requests_station_data_endpoint(session: Mock) -> None:
    response = Mock()
    response.json.return_value = {"data": []}
    session.get.return_value = response

    client = BerlinAirQualityClient(session=session)
    data = client.get_station_data("MC010")

    session.get.assert_called_once_with(
        "https://luftdaten.berlin.de/api/stations/MC010/data",
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    assert data == {"data": []}


def test_get_lqi_data_requests_official_lqi_data_endpoint(session: Mock) -> None:
    response = Mock()
    response.json.return_value = {"data": [{"station": "MC010", "lqi": 3}]}
    session.get.return_value = response

    client = BerlinAirQualityClient(session=session)
    data = client.get_lqi_data()

    session.get.assert_called_once_with(
        "https://luftdaten.berlin.de/api/lqis/data",
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    assert data == {"data": [{"station": "MC010", "lqi": 3}]}


def test_station_code_is_normalised_to_uppercase(session: Mock) -> None:
    response = Mock()
    response.json.return_value = {"data": []}
    session.get.return_value = response

    client = BerlinAirQualityClient(session=session)
    client.get_station_data("mc010")

    session.get.assert_called_once_with(
        "https://luftdaten.berlin.de/api/stations/MC010/data",
        timeout=10,
    )
