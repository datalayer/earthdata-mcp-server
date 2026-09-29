# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

"""Earthdata MCP Server: NASA Earthdata as a `reactor_mcp_server` extension."""

from earthdata_mcp_server.__version__ import __version__
from earthdata_mcp_server.extension import TOOLSET, EarthdataExtension

__all__ = ["TOOLSET", "EarthdataExtension", "__version__"]
