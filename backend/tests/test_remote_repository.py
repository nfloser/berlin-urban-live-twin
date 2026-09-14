"""Tests for direct SPARQL-backed repository operation."""

from pathlib import Path
from unittest.mock import patch

from rdflib import Graph

from app.repository import TwinRepository


def test_remote_repository_uses_sparql_store_without_downloading_graph(tmp_path: Path) -> None:
    remote_graph = Graph()
    remote_graph.parse(
        data="""
        @prefix city: <https://example.org/berlin/ontology/> .
        <https://example.org/station/CI001> a city:AirQualityStation ;
            city:stationCode "CI001" ;
            city:isActive true .
        """,
        format="turtle",
    )

    with patch("app.repository.create_remote_graph", return_value=remote_graph) as create:
        repository = TwinRepository(
            tmp_path,
            sparql_endpoint_url="http://fuseki:3030/twin/sparql",
        )
        repository.reload()

    create.assert_called_once_with("http://fuseki:3030/twin/sparql")
    assert repository.active_station_count() == 1


def test_file_backed_repository_does_not_create_remote_store(tmp_path: Path) -> None:
    (tmp_path / "state.ttl").write_text(
        '<https://example.org/a> <https://example.org/p> "value" .',
        encoding="utf-8",
    )

    with patch("app.repository.create_remote_graph") as create:
        repository = TwinRepository(tmp_path)
        repository.reload()

    create.assert_not_called()
    assert len(repository.graph) == 1
