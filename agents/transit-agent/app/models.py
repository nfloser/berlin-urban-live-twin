"""Domain models for public-transport realtime summaries."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TransitSnapshot:
    """Aggregated state derived from a GTFS-Realtime feed."""

    generated_at: datetime
    total_trip_updates: int
    delayed_trip_updates: int
    max_delay_seconds: int

    @property
    def delayed_share(self) -> float:
        """Fraction of trip updates with a delay above one minute."""
        if self.total_trip_updates == 0:
            return 0.0
        return self.delayed_trip_updates / self.total_trip_updates
