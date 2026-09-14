"""Domain models used by the air quality agent."""

from dataclasses import dataclass
from datetime import datetime


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


@dataclass(frozen=True, slots=True)
class AirQualityIndexObservation:
    """Official Berlin short-term air-quality index observation for one station."""

    station_code: str
    observed_at: datetime
    grade: int
    component_grades: dict[str, int]
