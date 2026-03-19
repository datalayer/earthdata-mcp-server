#!/usr/bin/env python3
"""CLI smoke tests for Earthdata MCP Server."""

import subprocess
import sys


def test_main_help() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "earthdata_mcp_server.server", "--help"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        return False

    expected = ["start"]
    missing = [cmd for cmd in expected if cmd not in result.stdout]
    if missing:
        print(f"Missing commands: {missing}")
        return False
    return True


def test_start_help_options() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "earthdata_mcp_server.server", "start", "--help"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        return False

    expected_options = ["--transport", "--port"]
    missing = [opt for opt in expected_options if opt not in result.stdout]
    if missing:
        print(f"Missing options: {missing}")
        return False
    return True


def main() -> int:
    tests = [test_main_help, test_start_help_options]
    results = [test() for test in tests]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
