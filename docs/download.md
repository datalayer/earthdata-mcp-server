# Download Workflow

This page explains how `download_earth_data_granules` works and how to combine Earthdata downloads with notebook execution.

## Tool behavior

The `download_earth_data_granules` tool always performs a granule search first, then executes one of three modes.

### Mode: `manifest`

- Returns search results as metadata only.
- No file download is performed.
- Use this to verify that your `short_name`, `temporal`, and `bounding_box` filters are correct.

### Mode: `download`

- Runs search and immediate download on the Earthdata MCP Server runtime.
- Writes files under `folder_name`.
- Uses Earthdata credentials from environment variables:
  - `EARTHDATA_USERNAME`
  - `EARTHDATA_PASSWORD`

### Mode: `script`

- Returns Python code that performs the same search and download.
- Does not execute the code in this server.
- Designed for execution by another runtime server (for example, Jupyter).

## Why compose with mcp-compose

Earthdata MCP Server is intentionally focused on Earthdata APIs.

If you need notebook-side execution and analysis, compose servers with `mcp-compose`:

- `earthdata-mcp-server` for discovery and download-script generation
- `jupyter-mcp-server` for notebook cell insertion/execution

This keeps each server focused while still enabling end-to-end workflows.

## Composition pattern

Recommended flow:

1. Call `download_earth_data_granules(..., mode="manifest")` to inspect scope.
2. Call `download_earth_data_granules(..., mode="script")` to get executable Python.
3. Use Jupyter MCP tools (via composed stack) to insert and run that script in a notebook.
4. Continue analysis in the same notebook session.

## Minimal mcp-compose idea

At a high level, define both servers in your mcp-compose setup and expose them to your MCP client as one composed surface.

- Earthdata server provides discovery/download script generation.
- Jupyter server provides notebook runtime operations.

Then your agent can orchestrate a single flow:

1. Discover dataset/granules with Earthdata tools.
2. Generate script with Earthdata `script` mode.
3. Execute script with Jupyter notebook tools.
4. Visualize and analyze results.
