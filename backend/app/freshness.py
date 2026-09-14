"""Freshness assessment for live urban-twin observations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

THRESHOLDS = {
    "air_quality": timedelta(hours=2),
    "weather": timedelta(hours=2),
    "transit": timedelta(minutes=15),
    "urban_stress": timedelta(hours=2),
}


def assess_freshness(
    timestamps: dict[str, datetime | None],
    *,
    now: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Return age and status for each source using explicit domain thresholds."""
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    result: dict[str, dict[str, Any]] = {}
    for source, threshold in THRESHOLDS.items():
        observed_at = timestamps.get(source)
        if observed_at is None:
            result[source] = {
                "status": "missing",
                "observed_at": None,
                "age_seconds": None,
                "threshold_seconds": int(threshold.total_seconds()),
            }
            continue
        if observed_at.tzinfo is None:
            raise ValueError(f"timestamp for {source} must be timezone-aware")

        age = max(timedelta(0), reference - observed_at.astimezone(timezone.utc))
        result[source] = {
            "status": "fresh" if age <= threshold else "stale",
            "observed_at": observed_at.isoformat(),
            "age_seconds": int(age.total_seconds()),
            "threshold_seconds": int(threshold.total_seconds()),
        }
    return result
