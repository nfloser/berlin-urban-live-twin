"""Tests for derived urban-stress calculations."""

import pytest

from app.urban_stress import calculate_urban_stress


def test_urban_stress_combines_environmental_and_transit_components() -> None:
    result = calculate_urban_stress(
        air_quality_grade=4,
        temperature_c=30.0,
        delayed_share=0.25,
    )

    assert result.air_quality_component == pytest.approx(0.6)
    assert result.heat_component == pytest.approx(2 / 3)
    assert result.transit_component == pytest.approx(0.5)
    assert result.index == pytest.approx(59.0)


def test_urban_stress_clamps_inputs_to_normalised_range() -> None:
    result = calculate_urban_stress(
        air_quality_grade=9,
        temperature_c=50.0,
        delayed_share=2.0,
    )

    assert result.air_quality_component == 1.0
    assert result.heat_component == 1.0
    assert result.transit_component == 1.0
    assert result.index == 100.0
