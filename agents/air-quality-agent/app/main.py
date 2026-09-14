"""Command-line entry point for the Berlin air-quality ingestion agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.agent import AirQualityAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh Berlin air-quality station metadata.")
    parser.add_argument("--output", type=Path, help="Optional Turtle output file.")
    return parser.parse_args()


def main() -> None:
    """Run one station-ingestion cycle and optionally persist the RDF graph."""
    args = parse_args()
    agent = AirQualityAgent()
    result = agent.refresh_stations()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        agent.knowledge_graph.graph.serialize(destination=args.output, format="turtle")

    print(
        f"Air-quality station refresh completed: "
        f"{result.ingested} ingested, {result.rejected} rejected."
    )


if __name__ == "__main__":
    main()
