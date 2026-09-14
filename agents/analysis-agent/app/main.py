"""Command-line entry point for cross-domain urban-stress derivation."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.live_analysis import derive_latest_urban_stress
from app.rdf_mapper import urban_stress_to_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive urban stress from persisted twin RDF state.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result, observed_at = derive_latest_urban_stress(args.data_dir)
    graph = urban_stress_to_graph(result, observed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=args.output, format="turtle")
    print(f"Urban stress refresh completed: index={result.index:.1f}")


if __name__ == "__main__":
    main()
