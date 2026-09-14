"""FastAPI interface for querying the current Berlin urban twin state."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from app.freshness import assess_freshness
from app.repository import TwinRepository


def create_app(
    data_directory: Path | None = None,
    graph_store_url: str | None = None,
) -> FastAPI:
    """Create the API application for a file-backed or Graph-Store-backed state."""
    directory = data_directory or Path(os.getenv("TWIN_DATA_DIR", "data"))
    configured_store = graph_store_url
    if configured_store is None and data_directory is None:
        configured_store = os.getenv("TWIN_GRAPH_STORE_URL")

    repository = TwinRepository(
        directory,
        graph_store_url=configured_store,
    )

    app = FastAPI(
        title="Berlin Urban Live Twin API",
        version="0.4.0",
        description="Query interface for the semantically integrated urban twin state.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:8080"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    def reload() -> None:
        repository.reload()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/state")
    def state() -> dict[str, int]:
        reload()
        return {
            "active_air_quality_stations": repository.active_station_count(),
            "triple_count": len(repository.graph),
        }

    @app.get("/freshness")
    def freshness() -> dict[str, dict[str, Any]]:
        reload()
        return assess_freshness(repository.latest_observation_timestamps())

    @app.get("/stations")
    def stations() -> list[dict[str, Any]]:
        reload()
        return repository.active_stations()

    @app.get("/air-quality")
    def air_quality() -> dict[str, Any]:
        reload()
        observation = repository.latest_air_quality()
        if observation is None:
            raise HTTPException(status_code=404, detail="No air-quality index observation available")
        return observation

    @app.get("/weather")
    def weather() -> dict[str, Any]:
        reload()
        observation = repository.latest_weather()
        if observation is None:
            raise HTTPException(status_code=404, detail="No weather observation available")
        return observation

    @app.get("/transit")
    def transit() -> dict[str, Any]:
        reload()
        observation = repository.latest_transit()
        if observation is None:
            raise HTTPException(status_code=404, detail="No transit observation available")
        return observation

    @app.get("/urban-stress")
    def urban_stress() -> dict[str, Any]:
        reload()
        observation = repository.latest_urban_stress()
        if observation is None:
            raise HTTPException(status_code=404, detail="No urban-stress observation available")
        return observation

    @app.get("/graph", response_class=Response)
    def graph() -> Response:
        reload()
        turtle = repository.graph.serialize(format="turtle")
        return Response(content=turtle, media_type="text/turtle")

    return app


app = create_app()
