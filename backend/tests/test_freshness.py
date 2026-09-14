"""Tests for explicit freshness assessment of live twin source observations."""

from datetime import datetime, timedelta, timezone

from app.freshness import assess_freshness


def test_assesses_domain_specific_freshness_thresholds() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)

    result = assess_freshness(
        {
            "air_quality": now - timedelta(minutes=70),
            "weather": now - timedelta(minutes=20),
            "transit": now - timedelta(minutes=10),
            "urban_stress": now - timedelta(minutes=5),
        },
        now=now,
    )

    assert result["air_quality"]["status"] == "fresh"
    assert result["weather"]["status"] == "fresh"
    assert result["transit"]["status"] == "fresh"
    assert result["urban_stress"]["status"] == "fresh"


def test_marks_stale_and_missing_sources_explicitly() -> None:
    now = datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc)

    result = assess_freshness(
        {
            "air_quality": now - timedelta(hours=3),
            "weather": None,
            "transit": now - timedelta(minutes=30),
            "urban_stress": now - timedelta(hours=4),
        },
        now=now,
    )

    assert result["air_quality"]["status"] == "stale"
    assert result["weather"]["status"] == "missing"
    assert result["transit"]["status"] == "stale"
    assert result["urban_stress"]["status"] == "stale"
