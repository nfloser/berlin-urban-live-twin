"""Tests for publishing the integrated RDF state to a Graph Store endpoint."""

from pathlib import Path
from unittest.mock import Mock

from rdflib import Graph

from scripts.publish_graph import publish_graph


def test_publish_graph_merges_turtle_files_and_replaces_default_graph(tmp_path: Path) -> None:
    (tmp_path / "air-quality.ttl").write_text(
        '<https://example.org/a> <https://example.org/p> "air" .',
        encoding="utf-8",
    )
    (tmp_path / "weather.ttl").write_text(
        '<https://example.org/w> <https://example.org/p> "weather" .',
        encoding="utf-8",
    )
    session = Mock()
    response = Mock()
    session.put.return_value = response

    triple_count = publish_graph(
        tmp_path,
        "http://fuseki:3030/twin/data?default",
        session=session,
    )

    assert triple_count == 2
    payload = session.put.call_args.kwargs["data"]
    graph = Graph().parse(data=payload, format="turtle")
    assert len(graph) == 2
    session.put.assert_called_once()
    assert session.put.call_args.args[0] == "http://fuseki:3030/twin/data?default"
    assert session.put.call_args.kwargs["headers"] == {"Content-Type": "text/turtle"}
    assert session.put.call_args.kwargs["timeout"] == 30
    response.raise_for_status.assert_called_once_with()
