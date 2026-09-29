# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""The ``earthdata-mcp-server`` HTTP app: the toolset on at ``/mcp``."""

from __future__ import annotations

from starlette.testclient import TestClient

from earthdata_mcp_server.server import earthdata_host, http_app


def test_toolsets_route_lists_earthdata_as_active() -> None:
    with TestClient(http_app(earthdata_host())) as client:
        answer = client.get("/toolsets").json()
    assert answer["active"] == ["earthdata"]
    assert "search_earth_datasets" in answer["tools"]


def test_a_browser_origin_is_allowed() -> None:
    with TestClient(http_app(earthdata_host())) as client:
        answer = client.options(
            "/mcp",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert answer.status_code == 200
    assert answer.headers["access-control-allow-origin"] in ("*", "https://example.com")
