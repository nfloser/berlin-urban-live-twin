"""Validate the integrated urban-twin RDF state against SHACL constraints."""

from __future__ import annotations

from pathlib import Path

from pyshacl import validate
from rdflib import Graph


def load_integrated_graph(data_directory: Path) -> Graph:
    graph = Graph()
    for path in sorted(data_directory.glob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


def validate_integrated_graph(data_directory: Path, shapes_path: Path) -> int:
    """Validate all persisted domain RDF and return the validated triple count.

    Raises ValueError with the SHACL report when the graph does not conform.
    """
    graph = load_integrated_graph(data_directory)
    shapes = Graph().parse(shapes_path, format="turtle")
    conforms, _, report = validate(
        data_graph=graph,
        shacl_graph=shapes,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )
    if not conforms:
        raise ValueError(f"Integrated RDF state failed SHACL validation:\n{report}")
    return len(graph)
