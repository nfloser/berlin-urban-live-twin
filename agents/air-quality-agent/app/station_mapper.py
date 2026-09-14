"""Mapping helpers for Berlin air-quality station payloads."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.models import AirQualityStation


def map_station(payload: Mapping[str, Any]) -> AirQualityStation:
    """Convert a raw Berlin API station payload into a domain object."""
    raw_code = payload.get("code")
    if not raw_code:
        raise ValueError("station payload is missing code")

    try:
        latitude = float(payload["lat"])
        longitude = float(payload["lng"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("station payload contains invalid coordinates") from exc

    groups = payload.get("stationgroups") or []

    return AirQualityStation(
        code=str(raw_code).strip().upper(),
        name=str(payload.get("name") or raw_code),
        latitude=latitude,
        longitude=longitude,
        address=payload.get("address"),
        active=bool(payload.get("active", False)),
        categories=tuple(str(group) for group in groups),
    )
