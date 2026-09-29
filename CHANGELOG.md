<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

# Changelog

## 0.5.0

- The server is now a [`reactor_mcp_server`](https://pypi.org/project/reactor-mcp-server/)
  extension. Installed beside any host of that foundation, it is discovered on the
  `reactor.mcp.extensions` entry-point group and served as the opt-in `earthdata`
  toolset (`/mcp?earthdata`). `earthdata-mcp-server start` still serves it on its
  own, over stdio or streamable HTTP.
- Requires the MCP Python SDK 2 (`mcp>=2,<3`) and `reactor_mcp_server>=1.0.4`.
- Every tool carries its annotations: the searches are read-only, and all three are
  idempotent and open-world.
- The tools no longer block the event loop: earthaccess runs in a worker thread.
- `search_earth_datasets` works with earthaccess 0.19, which turned `abstract`, `data_type` and
  `landing_page` into properties; it failed on a fresh install before.
- `start` takes `--host`.
- Releases are cut by pushing a `vX.Y.Z` tag, published to PyPI through trusted
  publishing. See RELEASE.md.
