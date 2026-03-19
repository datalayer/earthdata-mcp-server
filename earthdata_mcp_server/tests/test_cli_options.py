"""CLI unit tests for Earthdata MCP Server."""

from click.testing import CliRunner

from earthdata_mcp_server.server import server


def test_main_help() -> None:
    runner = CliRunner()
    result = runner.invoke(server, ["--help"])
    assert result.exit_code == 0, result.output
    assert "start" in result.output

    assert result.returncode == 0, result.stderr
    result = runner.invoke(server, ["start", "--help"])
    assert result.exit_code == 0, result.output
    assert "--transport" in result.output
    assert not missing, f"Missing commands: {missing}"


def test_start_help_options() -> None:





    assert result.returncode == 0, result.stderr



    assert not missing, f"Missing options: {missing}"




    all_passed = True
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            all_passed = False
            print(exc, file=sys.stderr)
    return 0 if all_passed else 1