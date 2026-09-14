"""Publish the integrated Turtle state to a SPARQL Graph Store endpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import requests
from rdflib import Graph


def publish_graph(
    data_directory: Path,
    graph_store_url: str,
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> int:
    """Merge all local Turtle outputs and replace the remote default graph."""
    graph = Graph()
    for path in sorted(data_directory.glob("*.ttl")):
        graph.parse(path, format="turtle")

    turtle = graph.serialize(format="turtle")
    client = session or requests.Session()
    response = client.put(
        graph_store_url,
        data=turtle,
        headers={"Content-Type": "text/turtle"},
        timeout=timeout,
    )
    response.raise_for_status()
    return len(graph)


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the integrated twin RDF graph.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--graph-store-url", required=True)
    args = parser.parse_args()

    triple_count = publish_graph(args.data_dir, args.graph_store_url)
    print(f"Published integrated RDF graph: {triple_count} triples")


if __name__ == "__main__":
    main()
