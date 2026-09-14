"""Tests for the top-level refresh orchestration script."""

from pathlib import Path
from unittest.mock import patch

from scripts.refresh_all import refresh_all


def test_refresh_all_runs_each_domain_agent_and_targets_shared_data_directory(tmp_path: Path) -> None:
    with patch("scripts.refresh_all.subprocess.run") as run:
        refresh_all(repo_root=tmp_path)

    assert run.call_count == 3
    working_directories = [Path(call.kwargs["cwd"]).name for call in run.call_args_list]
    assert working_directories == ["air-quality-agent", "weather-agent", "transit-agent"]

    output_arguments = [call.args[0][-1] for call in run.call_args_list]
    assert output_arguments == [
        str(tmp_path / "data" / "air-quality.ttl"),
        str(tmp_path / "data" / "weather.ttl"),
        str(tmp_path / "data" / "transit.ttl"),
    ]
