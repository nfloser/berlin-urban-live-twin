"""Run all domain ingestion agents and persist their RDF outputs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


AGENTS = (
    ("air-quality-agent", "air-quality.ttl"),
    ("weather-agent", "weather.ttl"),
    ("transit-agent", "transit.ttl"),
)


def refresh_all(repo_root: Path | None = None) -> None:
    """Execute each agent sequentially and write RDF into the shared data directory."""
    root = repo_root or Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for agent_name, output_name in AGENTS:
        agent_dir = root / "agents" / agent_name
        environment = os.environ.copy()
        environment["PYTHONPATH"] = "."
        subprocess.run(
            [
                sys.executable,
                "-m",
                "app.main",
                "--output",
                str(data_dir / output_name),
            ],
            cwd=agent_dir,
            env=environment,
            check=True,
        )


if __name__ == "__main__":
    refresh_all()
