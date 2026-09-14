"""Tests for retrieving current DWD-derived weather data for Berlin."""

from unittest.mock import Mock

from app.weather_client import BrightSkyWeatherClient


def test_get_current_weather_requests_berlin_coordinates() -> None:
    session = Mock()
    response = Mock()
    response.json.return_value = {"weather": {"temperature": 18.2}}
    session.get.return_value = response

    client = BrightSkyWeatherClient(session=session)
    payload = client.get_current_weather()

    session.get.assert_called_once_with(
        "https://api.brightsky.dev/current_weather",
        params={"lat": 52.52, "lon": 13.405},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    assert payload == {"weather": {"temperature": 18.2}}
