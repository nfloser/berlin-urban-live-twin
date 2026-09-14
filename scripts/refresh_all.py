"""Run all ingestion agents and derive the shared urban-twin state."""

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


def _run(command: list[str], cwd: Path) -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "."
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def refresh_all(repo_root: Path | None = None) -> None:
    """Refresh source domains first, then derive cross-domain information."""
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


if __name__ == "__main__":
    refresh_all()
