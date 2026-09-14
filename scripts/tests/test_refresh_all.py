"""Tests for the top-level refresh orchestration script."""

from pathlib import Path
from unittest.mock import patch

from scripts.refresh_all import refresh_all


def test_refresh_all_runs_domain_agents_then_analysis_agent(tmp_path: Path) -> None:
    with patch("scripts.refresh_all.subprocess.run") as run:
        refresh_all(repo_root=tmp_path)

    assert run.call_count == 4
    working_directories = [Path(call.kwargs["cwd"]).name for call in run.call_args_list]
    assert working_directories == [
        "air-quality-agent",
        "weather-agent",
        "transit-agent",
        "analysis-agent",
    ]

    domain_output_arguments = [call.args[0][-1] for call in run.call_args_list[:3]]
    assert domain_output_arguments == [
        str(tmp_path / "data" / "air-quality.ttl"),
        str(tmp_path / "data" / "weather.ttl"),
        str(tmp_path / "data" / "transit.ttl"),
    ]

    analysis_command = run.call_args_list[3].args[0]
    assert analysis_command[-4:] == [
        "--data-dir",
        str(tmp_path / "data"),
        "--output",
        str(tmp_path / "data" / "urban-stress.ttl"),
    ]


def test_refresh_all_publishes_integrated_graph_when_store_url_is_configured(tmp_path: Path) -> None:
    with (
        patch("scripts.refresh_all.subprocess.run"),
        patch("scripts.refresh_all.publish_graph", return_value=42) as publish,
    ):
        result = refresh_all(
            repo_root=tmp_path,
            graph_store_url="http://fuseki:3030/twin/data?default",
        )

    publish.assert_called_once_with(
        tmp_path / "data",
        "http://fuseki:3030/twin/data?default",
    )
    assert result == 42
