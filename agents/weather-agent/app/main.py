"""Command-line entry point for Berlin weather ingestion."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.agent import WeatherAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh current Berlin weather data.")
    parser.add_argument("--output", type=Path, help="Optional Turtle output file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    graph = WeatherAgent().refresh()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(destination=args.output, format="turtle")

    print(f"Weather refresh completed: {len(graph)} RDF triples generated.")


if __name__ == "__main__":
    main()
