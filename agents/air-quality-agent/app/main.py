"""Command-line entry point for the Berlin air-quality ingestion agent."""

from app.agent import AirQualityAgent


def main() -> None:
    """Run one station-ingestion cycle and report its result."""
    result = AirQualityAgent().refresh_stations()
    print(
        f"Air-quality station refresh completed: "
        f"{result.ingested} ingested, {result.rejected} rejected."
    )


if __name__ == "__main__":
    main()
