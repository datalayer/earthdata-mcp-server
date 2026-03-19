"""CLI unit tests for Earthdata MCP Server."""

from click.testing import CliRunner

from earthdata_mcp_server.server import server


def test_main_help() -> None:
    runner = CliRunner()
    result = runner.invoke(server, ["--help"])
    assert result.exit_code == 0, result.output
    assert "start" in result.output


def test_start_help_options() -> None:
    runner = CliRunner()
    result = runner.invoke(server, ["start", "--help"])
    assert result.exit_code == 0, result.output
    assert "--transport" in result.output
    assert "--port" in result.output
