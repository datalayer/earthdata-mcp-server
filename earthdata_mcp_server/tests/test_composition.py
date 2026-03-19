#!/usr/bin/env python3
"""Smoke tests for Earthdata MCP Server tool registration and download modes."""

import sys


def test_tool_registration() -> bool:
    from earthdata_mcp_server.server import mcp

    tools = list(mcp._tool_manager._tools.keys())
    expected_tools = {
        "search_earth_datasets",
        "search_earth_datagranules",
        "download_earth_data_granules",
    }

    missing = sorted(expected_tools.difference(tools))
    if missing:
        print(f"Missing expected tools: {missing}")
        return False

    print(f"Registered tools ({len(tools)}): {tools}")
    return True


def test_download_mode_validation() -> bool:
    from earthdata_mcp_server import server as earthdata_server

    try:
        earthdata_server.download_earth_data_granules(
            folder_name="downloads/test",
            short_name="TEST",
            count=1,
            mode="invalid-mode",
        )
    except ValueError:
        print("Invalid mode correctly rejected")
        return True

    print("Invalid mode was not rejected")
    return False


def main() -> int:
    tests = [test_tool_registration, test_download_mode_validation]
    results = [test() for test in tests]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
