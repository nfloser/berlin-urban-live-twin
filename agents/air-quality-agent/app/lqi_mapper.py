"""Mapping helpers for official Berlin LQI payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.models import AirQualityIndexObservation

_COMPONENT_ALIASES = {
    "pm10": "PM10",
    "pm2.5": "PM2.5",
    "pm25": "PM2.5",
    "pm2_5": "PM2.5",
    "no2": "NO2",
    "o3": "O3",
    "co": "CO",
    "so2": "SO2",
}


def _first(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _grade(value: Any) -> int:
    grade = int(value)
    if grade < 1 or grade > 6:
        raise ValueError("LQI grade must be between 1 and 6")
    return grade


def _station_code(payload: dict[str, Any]) -> str:
    value = _first(payload, "station", "station_code", "stationCode", "code")
    if isinstance(value, dict):
        value = _first(value, "code", "station_code", "stationCode")
    code = str(value or "").strip().upper()
    if not code:
        raise ValueError("LQI observation requires a station code")
    return code


def _timestamp(payload: dict[str, Any]) -> datetime:
    value = _first(payload, "timestamp", "date", "datetime", "observed_at", "observedAt")
    if not value:
        raise ValueError("LQI observation requires a timestamp")
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("LQI timestamp must include a timezone")
    return parsed


def _component_grades(payload: dict[str, Any]) -> dict[str, int]:
    values: dict[str, Any] = {}
    nested = payload.get("components")
    if isinstance(nested, dict):
        values.update(nested)

    for alias in _COMPONENT_ALIASES:
        if alias in payload:
            values[alias] = payload[alias]

    result: dict[str, int] = {}
    for key, value in values.items():
        if value in (None, "", "-", "×", "U"):
            continue
        canonical = _COMPONENT_ALIASES.get(str(key).lower())
        if canonical:
            result[canonical] = _grade(value)
    return result


def map_lqi_observation(payload: dict[str, Any]) -> AirQualityIndexObservation:
    """Map one API record to the stable internal LQI domain model."""
    if not isinstance(payload, dict):
        raise TypeError("LQI payload must be a dictionary")

    return AirQualityIndexObservation(
        station_code=_station_code(payload),
        observed_at=_timestamp(payload),
        grade=_grade(_first(payload, "lqi", "index", "grade", "value")),
        component_grades=_component_grades(payload),
    )


def extract_lqi_records(payload: Any) -> list[dict[str, Any]]:
    """Extract record dictionaries from common API envelope variants."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "lqis"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise ValueError("Unsupported Berlin LQI response envelope")
