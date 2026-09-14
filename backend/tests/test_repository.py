"""Tests for loading the persisted semantic twin state."""

from pathlib import Path

from app.repository import TwinRepository


def test_repository_loads_all_turtle_files(tmp_path: Path) -> None:
    (tmp_path / "air.ttl").write_text(
        """
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/station/MC010> a city:AirQualityStation ;
            city:stationCode "MC010" ;
            city:isActive true .
        """,
        encoding="utf-8",
    )
    (tmp_path / "weather.ttl").write_text(
        """
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/weather/1> a city:WeatherObservation ;
            city:temperatureCelsius 18.2 .
        """,
        encoding="utf-8",
    )

    repository = TwinRepository(tmp_path)
    repository.reload()

    assert len(repository.graph) == 5
    assert repository.active_station_count() == 1
