"""Run all ingestion agents, derive state, and optionally publish it."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.publish_graph import publish_graph


AGENTS = (
    ("air-quality-agent", "air-quality.ttl"),
    ("weather-agent", "weather.ttl"),
    ("transit-agent", "transit.ttl"),
)


def _run(command: list[str], cwd: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "."
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def refresh_all(
    repo_root: Path | None = None,
    graph_store_url: str | None = None,
) -> int | None:
    """Refresh sources, derive information, then publish the integrated graph if configured."""
    root = repo_root or Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for agent_name, output_name in AGENTS:
        agent_dir = root / "agents" / agent_name
        _run(
            [
                sys.executable,
                "-m",
                "app.main",
                "--output",
                str(data_dir / output_name),
            ],
            cwd=agent_dir,
        )

    _run(
        [
            sys.executable,
            "-m",
            "app.main",
            "--data-dir",
            str(data_dir),
            "--output",
            str(data_dir / "urban-stress.ttl"),
        ],
        cwd=root / "agents" / "analysis-agent",
    )

    target = graph_store_url or os.getenv("TWIN_GRAPH_STORE_URL")
    if target:
        return publish_graph(data_dir, target)
    return None


if __name__ == "__main__":
    published = refresh_all()
    if published is not None:
        print(f"SPARQL store publication completed: {published} triples")
