"""Domain models used by the air quality agent."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AirQualityStation:
    """Normalised representation of a Berlin air-quality monitoring station."""

    code: str
    name: str
    latitude: float
    longitude: float
    address: str | None
    active: bool
    categories: tuple[str, ...]
