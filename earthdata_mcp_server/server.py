# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""The ``earthdata-mcp-server`` command: the Earthdata extension, served alone.

The tools live in :mod:`earthdata_mcp_server.extension`, as a
`reactor_mcp_server` extension. This command builds a host with that one
extension on it — the toolset on by default, since there is nothing else to
choose — and serves it over stdio or streamable HTTP.

To serve Earthdata beside other extensions, install this package next to any
`reactor_mcp_server` host instead; it is discovered there and served to a
client that asks for it (``/mcp?earthdata``).

@module earthdata_mcp_server.server
"""

from __future__ import annotations

import logging

import click
from reactor_mcp_server import McpHost, build_host, create_mcp_app
from starlette.applications import Starlette

from earthdata_mcp_server.extension import EarthdataExtension

logger = logging.getLogger(__name__)

#: What the server calls itself to a client.
SERVER_NAME = "earthdata"


def earthdata_host() -> McpHost:
    """A started host serving the Earthdata toolset, on without asking."""
    return build_host([EarthdataExtension(default=True)], name=SERVER_NAME)


def http_app(host: McpHost, path: str = "/mcp") -> Starlette:
    """The host over streamable HTTP, open to browser clients.

    CORS is on for any origin: a browser-based MCP client served from another
    origin cannot connect otherwise. A deployment exposed beyond one machine
    should put this behind a proxy that decides who may reach it.
    """
    from starlette.middleware.cors import CORSMiddleware

    app = create_mcp_app(host, path=path)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
    return app


@click.group()
def server() -> None:
    """Manages Earthdata MCP Server."""


@server.command("start")
@click.option(
    "--transport",
    envvar="TRANSPORT",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="The transport to use for the MCP server. Defaults to 'stdio'.",
)
@click.option(
    "--host",
    "bind",
    envvar="HOST",
    default="0.0.0.0",  # noqa: S104 - a server, reached from outside its container
    help="The interface to bind for the Streamable HTTP transport.",
)
@click.option(
    "--port",
    envvar="PORT",
    type=click.INT,
    default=4040,
    help="The port to use for the Streamable HTTP transport. Ignored for stdio transport.",
)
def start_command(transport: str, bind: str, port: int) -> None:
    """Start the Earthdata MCP server with a transport."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Earthdata MCP Server with transport: %s", transport)
    host = earthdata_host()

    if transport == "stdio":
        built = host.build()
        logger.info("Available tools: %s", list(built.tool_names))
        built.server.run(transport="stdio")
        return

    import uvicorn

    uvicorn.run(http_app(host), host=bind, port=port)


if __name__ == "__main__":
    server()
