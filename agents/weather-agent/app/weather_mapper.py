"""Mapping helpers for Bright Sky current-weather payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from app.models import WeatherObservation


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def map_current_weather(payload: Mapping[str, Any]) -> WeatherObservation:
    """Convert a Bright Sky payload into the internal weather model."""
    weather = payload.get("weather")
    if not isinstance(weather, Mapping):
        raise ValueError("payload is missing weather object")

    timestamp = weather.get("timestamp")
    if not timestamp:
        raise ValueError("weather object is missing timestamp")

    return WeatherObservation(
        observed_at=datetime.fromisoformat(str(timestamp)),
        temperature_c=_optional_float(weather.get("temperature")),
        relative_humidity_pct=_optional_float(weather.get("relative_humidity")),
        pressure_hpa=_optional_float(weather.get("pressure_msl")),
        wind_speed_kmh=_optional_float(weather.get("wind_speed")),
        condition=str(weather["condition"]) if weather.get("condition") is not None else None,
    )
