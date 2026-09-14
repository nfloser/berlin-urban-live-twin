"""FastAPI interface for querying the current Berlin urban twin state."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Response

from app.repository import TwinRepository


def create_app(data_directory: Path | None = None) -> FastAPI:
    """Create the API application for a given persisted RDF data directory."""
    directory = data_directory or Path(os.getenv("TWIN_DATA_DIR", "data"))
    repository = TwinRepository(directory)

    app = FastAPI(
        title="Berlin Urban Live Twin API",
        version="0.1.0",
        description="Query interface for the semantically integrated urban twin state.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/state")
    def state() -> dict[str, int]:
        repository.reload()
        return {
            "active_air_quality_stations": repository.active_station_count(),
            "triple_count": len(repository.graph),
        }

    @app.get("/graph", response_class=Response)
    def graph() -> Response:
        repository.reload()
        turtle = repository.graph.serialize(format="turtle")
        return Response(content=turtle, media_type="text/turtle")

    return app


app = create_app()
