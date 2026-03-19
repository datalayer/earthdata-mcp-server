<!--
  ~ Copyright (c) 2023-2024 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

[![Datalayer](https://assets.datalayer.tech/datalayer-25.svg)](https://datalayer.io)

[![Become a Sponsor](https://img.shields.io/static/v1?label=Become%20a%20Sponsor&message=%E2%9D%A4&logo=GitHub&style=flat&color=1ABC9C)](https://github.com/sponsors/datalayer)

# 🪐 ✨ Earthdata MCP Server

[![PyPI - Version](https://img.shields.io/pypi/v/earthdata-mcp-server)](https://pypi.org/project/earthdata-mcp-server)
[![smithery badge](https://smithery.ai/badge/@datalayer/earthdata-mcp-server)](https://smithery.ai/server/@datalayer/earthdata-mcp-server)

Earthdata MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server implementation that provides tools to interact with [NASA Earth Data](https://www.earthdata.nasa.gov/).

This server is intentionally Earthdata-only.

If you need notebook/runtime tools, compose this server with `jupyter-mcp-server` using [mcp-compose](https://github.com/datalayer/mcp-compose).

## Key Features

- Dataset discovery on NASA Earthdata
- Granule search with temporal and bounding box filters
- Flexible download workflow with explicit execution modes

<div>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <p>Analyzing Sea Level Rise with AI-Powered Geospatial Tools and Jupyter - Watch Video</p>
  </a>
  <a href="https://www.loom.com/share/c2b5b05f548d4f1492d5c107f0c48dbc">
    <img style="max-width:100%;" src="https://cdn.loom.com/sessions/thumbnails/c2b5b05f548d4f1492d5c107f0c48dbc-598a84f02de7e74e-full-play.gif">
  </a>
</div>

## Getting Started

### Local install

```bash
pip install earthdata-mcp-server
```

### Docker with Claude Desktop

```json
{
  "mcpServers": {
    "earthdata": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "datalayer/earthdata-mcp-server:latest"
      ],
      "env": {
        "EARTHDATA_USERNAME": "your_username",
        "EARTHDATA_PASSWORD": "your_password"
      }
    }
  }
}
```

### Linux host networking

```json
{
  "mcpServers": {
    "earthdata": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network=host",
        "datalayer/earthdata-mcp-server:latest"
      ],
      "env": {
        "EARTHDATA_USERNAME": "your_username",
        "EARTHDATA_PASSWORD": "your_password"
      }
    }
  }
}
```

## Tools

The server offers 3 Earthdata tools.

### `search_earth_datasets`

- Search for datasets on NASA Earthdata.
- Input:
  - search_keywords (str): Keywords to search for in the dataset titles.
  - count (int): Number of datasets to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of dataset abstracts.

### `search_earth_datagranules`

- Search for data granules on NASA Earthdata.
- Input:
  - short_name (str): Short name of the dataset.
  - count (int): Number of data granules to return.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
- Returns: List of data granules.

### `download_earth_data_granules`

- Search and optionally download granules with explicit modes.
- **Authentication**: Requires NASA Earthdata Login credentials (see [authentication guide](./docs/authentication.md))
- Input:
  - folder_name (str): Local folder name to save the data.
  - short_name (str): Short name of the Earth dataset to download.
  - count (int): Number of data granules to download.
  - temporal (tuple): (Optional) Temporal range in the format (date_from, date_to).
  - bounding_box (tuple): (Optional) Bounding box in the format (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).
  - mode (str): One of:
    - `manifest`: Returns granule metadata only.
    - `download`: Downloads files directly on server side.
    - `script`: Returns Python code to execute elsewhere.
  - max_manifest_items (int): Max items returned in `manifest` mode.

#### Recommended download strategy

1. Use `mode="manifest"` first to inspect results safely.
2. Use `mode="script"` when you want notebook-driven execution via `mcp-compose` + `jupyter-mcp-server`.
3. Use `mode="download"` only when server-side file writes are intended.

## Prompts

1. `download_analyze_global_sea_level`
   - Generates a workflow that starts with `download_earth_data_granules` in `script` mode.
   - Intended to be executed in a composed notebook/runtime stack (via `mcp-compose`).

2. `sealevel_rise_dataset`
   - Search for datasets related to sea level rise worldwide.
   - Input:
     - `start_year` (int): Start year to consider.
      - `end_year` (int): End year to consider.
   - Returns: Prompt correctly formatted.

3. `ask_datasets_format`
    - To ask about the format of the datasets.
    - Returns: Prompt correctly formatted.

## Building

```bash
# or run `docker build -t datalayer/earthdata-mcp-server .`
make build-docker
```

If you prefer, you can pull the prebuilt images.

```bash
make pull-docker
```
