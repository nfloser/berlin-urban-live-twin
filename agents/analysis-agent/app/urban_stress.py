"""Derived urban-stress calculation across environmental and mobility domains."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UrbanStressResult:
    """Normalised component scores and the resulting composite index."""

    air_quality_component: float
    heat_component: float
    transit_component: float
    index: float


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(value, upper))


def calculate_urban_stress(
    *,
    air_quality_grade: float,
    temperature_c: float,
    delayed_share: float,
) -> UrbanStressResult:
    """Calculate a 0-100 exploratory urban-stress index.

    The index is intentionally transparent rather than predictive. It combines
    three normalised components using explicit weights so that the derivation
    can be inspected and challenged later.
    """
    air = _clamp((air_quality_grade - 1.0) / 5.0)
    heat = _clamp((temperature_c - 20.0) / 15.0)
    transit = _clamp(delayed_share / 0.5)

    index = 100.0 * ((0.4 * air) + (0.3 * heat) + (0.3 * transit))

    return UrbanStressResult(
        air_quality_component=air,
        heat_component=heat,
        transit_component=transit,
        index=index,
    )
