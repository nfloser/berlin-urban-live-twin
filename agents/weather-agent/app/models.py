"""Domain model for weather observations."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WeatherObservation:
    """Normalised current weather observation for Berlin."""

    observed_at: datetime
    temperature_c: float | None
    relative_humidity_pct: float | None
    pressure_hpa: float | None
    wind_speed_kmh: float | None
    condition: str | None
