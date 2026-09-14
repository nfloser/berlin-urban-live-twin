"""Tests for the top-level refresh orchestration script."""

from pathlib import Path
from unittest.mock import patch

from scripts.refresh_all import refresh_all


def test_refresh_all_runs_each_domain_agent_and_targets_shared_data_directory(tmp_path: Path) -> None:
    with patch("scripts.refresh_all.subprocess.run") as run:
        refresh_all(repo_root=tmp_path)

    assert run.call_count == 3
    commands = [call.args[0] for call in run.call_args_list]
    assert any("air-quality-agent" in str(command) for command in commands)
    assert any("weather-agent" in str(command) for command in commands)
    assert any("transit-agent" in str(command) for command in commands)
